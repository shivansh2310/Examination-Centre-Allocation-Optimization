import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .config import PLOTS_DIR


Color = tuple[int, int, int]

INK = (30, 30, 30)
AXIS = (70, 70, 70)
GRID = (220, 220, 220)
BLUE = (31, 119, 180)
ORANGE = (255, 127, 14)
GREEN = (44, 160, 44)
RED = (214, 39, 40)


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        "LiberationSans-Bold.ttf" if bold else "LiberationSans-Regular.ttf",
        "NotoSans-Bold.ttf" if bold else "NotoSans-Regular.ttf",
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
    )
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


TITLE_FONT = _font(24, bold=True)
LABEL_FONT = _font(18)
TICK_FONT = _font(15)
VALUE_FONT = _font(14)
LEGEND_FONT = _font(16)


def _text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def _nice_upper(values: list[float]) -> float:
    maximum = max(values) if values else 1
    if maximum <= 0:
        return 1
    magnitude = 10 ** math.floor(math.log10(maximum))
    scaled = maximum / magnitude
    if scaled <= 2:
        nice = 2
    elif scaled <= 5:
        nice = 5
    else:
        nice = 10
    return nice * magnitude


def _format_value(value: float, percent: bool = False) -> str:
    if percent:
        return f"{value:.1f}%"
    if abs(value) >= 100:
        return f"{value:.0f}"
    return f"{value:.1f}"


def _save_png(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, "PNG", dpi=(300, 300))


def _draw_line_chart(
    path: Path,
    title: str,
    y_label: str,
    x_labels: list[str],
    series: list[tuple[str, list[float], Color]],
    percent: bool = False,
) -> None:
    width, height = 1200, 760
    margin_left, margin_right = 120, 70
    margin_top, margin_bottom = 100, 125
    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom

    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    all_values = [value for _, values, _ in series for value in values]
    y_max = 100 if percent else _nice_upper(all_values)
    y_min = 0

    title_width, _ = _text_size(draw, title, TITLE_FONT)
    draw.text(((width - title_width) / 2, 28), title, fill=INK, font=TITLE_FONT)

    for tick in range(6):
        value = y_min + (y_max - y_min) * tick / 5
        y = margin_top + plot_height - ((value - y_min) / (y_max - y_min)) * plot_height
        draw.line((margin_left, y, width - margin_right, y), fill=GRID, width=1)
        tick_label = _format_value(value, percent=percent)
        tw, th = _text_size(draw, tick_label, TICK_FONT)
        draw.text((margin_left - tw - 12, y - th / 2), tick_label, fill=INK, font=TICK_FONT)

    draw.line((margin_left, margin_top, margin_left, margin_top + plot_height), fill=AXIS, width=2)
    draw.line(
        (margin_left, margin_top + plot_height, width - margin_right, margin_top + plot_height),
        fill=AXIS,
        width=2,
    )

    x_positions = [
        margin_left + index * plot_width / max(1, len(x_labels) - 1)
        for index in range(len(x_labels))
    ]
    for x, label in zip(x_positions, x_labels, strict=True):
        draw.line((x, margin_top + plot_height, x, margin_top + plot_height + 7), fill=AXIS, width=1)
        display = label.replace("_", " ").title()
        tw, th = _text_size(draw, display, TICK_FONT)
        draw.text((x - tw / 2, margin_top + plot_height + 18), display, fill=INK, font=TICK_FONT)

    x_label = "Allocation / Scenario"
    tw, _ = _text_size(draw, x_label, LABEL_FONT)
    draw.text(((width - tw) / 2, height - 48), x_label, fill=INK, font=LABEL_FONT)
    draw.text((24, margin_top - 35), y_label, fill=INK, font=LABEL_FONT)

    legend_x = width - margin_right - 260
    legend_y = 73
    for index, (name, _, color) in enumerate(series):
        y = legend_y + index * 28
        draw.line((legend_x, y + 9, legend_x + 36, y + 9), fill=color, width=3)
        draw.ellipse((legend_x + 13, y + 4, legend_x + 23, y + 14), fill=color)
        draw.text((legend_x + 48, y), name, fill=INK, font=LEGEND_FONT)

    for _, values, color in series:
        points = []
        for x, value in zip(x_positions, values, strict=True):
            y = margin_top + plot_height - ((value - y_min) / (y_max - y_min)) * plot_height
            points.append((x, y, value))
        if len(points) > 1:
            draw.line([(x, y) for x, y, _ in points], fill=color, width=3)
        for index, (x, y, value) in enumerate(points):
            draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=color)
            label = _format_value(value, percent=percent)
            tw, th = _text_size(draw, label, VALUE_FONT)
            label_x = x - tw / 2
            if index == 0:
                label_x = x + 8
            elif index == len(points) - 1:
                label_x = x - tw - 8
            draw.text((label_x, y - th - 10), label, fill=INK, font=VALUE_FONT)

    _save_png(image, path)


def _draw_sensitivity_panels(path: Path, sensitivity_metrics: list[dict]) -> None:
    width, height = 1400, 1000
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    title = "Sensitivity Analysis Across Objective Weighting Scenarios"
    tw, _ = _text_size(draw, title, TITLE_FONT)
    draw.text(((width - tw) / 2, 28), title, fill=INK, font=TITLE_FONT)

    panels = [
        ("Average distance", "Distance", "avg_distance", BLUE, False),
        ("Average hardship", "Hardship", "avg_hardship", RED, False),
        ("First preference rate", "Rate", "first_preference_rate", GREEN, True),
        ("Outside preference rate", "Rate", "outside_preference_rate", ORANGE, True),
    ]
    labels = [row["allocation"].replace("_", " ").title() for row in sensitivity_metrics]

    panel_w, panel_h = 610, 365
    origins = [(85, 105), (745, 105), (85, 555), (745, 555)]
    for (panel_title, y_label, key, color, percent), (x0, y0) in zip(panels, origins, strict=True):
        values = [float(row[key]) * 100 if percent else float(row[key]) for row in sensitivity_metrics]
        y_max = 100 if percent else _nice_upper(values)
        plot_left, plot_top = x0 + 78, y0 + 55
        plot_w, plot_h = panel_w - 110, panel_h - 120

        draw.rectangle((x0, y0, x0 + panel_w, y0 + panel_h), outline=(235, 235, 235), width=1)
        draw.text((x0 + 22, y0 + 18), panel_title, fill=INK, font=LABEL_FONT)

        for tick in range(5):
            value = y_max * tick / 4
            y = plot_top + plot_h - (value / y_max) * plot_h
            draw.line((plot_left, y, plot_left + plot_w, y), fill=GRID, width=1)
            tick_label = _format_value(value, percent=percent)
            tw_tick, th_tick = _text_size(draw, tick_label, TICK_FONT)
            draw.text((plot_left - tw_tick - 10, y - th_tick / 2), tick_label, fill=INK, font=TICK_FONT)

        draw.line((plot_left, plot_top, plot_left, plot_top + plot_h), fill=AXIS, width=2)
        draw.line((plot_left, plot_top + plot_h, plot_left + plot_w, plot_top + plot_h), fill=AXIS, width=2)

        x_positions = [
            plot_left + index * plot_w / max(1, len(values) - 1)
            for index in range(len(values))
        ]
        points = []
        for x, value in zip(x_positions, values, strict=True):
            y = plot_top + plot_h - (value / y_max) * plot_h
            points.append((x, y, value))
        draw.line([(x, y) for x, y, _ in points], fill=color, width=3)

        for index, (x, y, value) in enumerate(points):
            draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=color)
            value_label = _format_value(value, percent=percent)
            tw_value, th_value = _text_size(draw, value_label, VALUE_FONT)
            label_x = x - tw_value / 2
            if index == 0:
                label_x = x + 8
            elif index == len(points) - 1:
                label_x = x - tw_value - 8
            draw.text((label_x, y - th_value - 8), value_label, fill=INK, font=VALUE_FONT)

        for x, label in zip(x_positions, labels, strict=True):
            words = label.split()
            line1 = " ".join(words[:1])
            line2 = " ".join(words[1:])
            for offset, line in enumerate([line1, line2]):
                tw_label, _ = _text_size(draw, line, TICK_FONT)
                draw.text((x - tw_label / 2, plot_top + plot_h + 15 + offset * 18), line, fill=INK, font=TICK_FONT)

    _save_png(image, path)


def create_plots(
    baseline_metrics: dict,
    optimized_metrics: dict,
    sensitivity_metrics: list[dict] | None = None,
) -> None:
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    comparison_labels = ["Baseline", "Optimized"]

    _draw_line_chart(
        PLOTS_DIR / "distance_comparison.png",
        "Average Distance: Baseline vs Optimized Allocation",
        "Average distance",
        comparison_labels,
        [
            (
                "Average distance",
                [baseline_metrics["avg_distance"], optimized_metrics["avg_distance"]],
                BLUE,
            )
        ],
    )
    _draw_line_chart(
        PLOTS_DIR / "preference_satisfaction.png",
        "First Preference Satisfaction: Baseline vs Optimized Allocation",
        "Percentage",
        comparison_labels,
        [
            (
                "First preference",
                [
                    baseline_metrics["first_preference_rate"] * 100,
                    optimized_metrics["first_preference_rate"] * 100,
                ],
                GREEN,
            )
        ],
        percent=True,
    )
    _draw_line_chart(
        PLOTS_DIR / "hardship_comparison.png",
        "Average Hardship: Baseline vs Optimized Allocation",
        "Average hardship",
        comparison_labels,
        [
            (
                "Average hardship",
                [baseline_metrics["avg_hardship"], optimized_metrics["avg_hardship"]],
                RED,
            )
        ],
    )

    if sensitivity_metrics:
        _draw_sensitivity_panels(PLOTS_DIR / "sensitivity_comparison.png", sensitivity_metrics)
