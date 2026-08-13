import matplotlib as mpl

STATION_STYLE_MAP = {
    "강남소방서": {"area": "서울", "color": "#1F4E79", "marker": "o",
                "linestyle": "-", "hatch": ""},
    "강동소방서": {"area": "서울", "color": "#C8791F", "marker": "s",
                "linestyle": "--", "hatch": "//"},
    "노원소방서": {"area": "서울", "color": "#2E7D5B", "marker": "^",
                "linestyle": ":", "hatch": ".."},
    "수성소방서": {"area": "대구", "color": "#9A3324", "marker": "D",
                "linestyle": "-", "hatch": "xx"},
    "해운대소방서": {"area": "부산", "color": "#6B5B95", "marker": "v",
                 "linestyle": "--", "hatch": "\\\\"},
    "원주소방서": {"area": "원주", "color": "#A34A78", "marker": "P",
                "linestyle": "-.", "hatch": "++"}
}

OVERALL_COLOR = "#7A828C"
REFERENCE_COLOR = "#333333"

FONT_SIZES = {
    "font.size": 15,
    "axes.titlesize": 19,
    "axes.labelsize": 16,
    "xtick.labelsize": 14,
    "ytick.labelsize": 14,
    "legend.fontsize": 15,
    "figure.titlesize": 21
}

def apply_plot_style() -> None:
    """
    Note: Call after importing koreanize_matplotlib so the Korean font stays.
    """
    mpl.rcParams.update(FONT_SIZES)
    
    mpl.rcParams.update({
        "axes.grid": True,
        "grid.alpha": 0.25,
        "axes.edgecolor": "#444444",
        "hatch.linewidth": 0.6,
        "savefig.facecolor": "white",
        "figure.facecolor": "white"
        })
    
    mpl.rcParams.update({
        "axes.linewidth": 1.6,
        "xtick.direction": "in",
        "ytick.direction": "in",
        "xtick.top": True,
        "ytick.right": True,
        "xtick.major.size": 5,
        "ytick.major.size": 5,
        "xtick.major.width": 1.0,
        "ytick.major.width": 1.0
        })

def set_bin_edge_ticks(axis, bin_edges: list, first_edge_position: float,
                       step: float = 1.0) -> None:
    """
    Puts ticks on the bin boundaries with one number each, so a binned
    temperature axis reads as a continuous scale instead of as categories.

    first_edge_position: x of the leftmost boundary. Line plots drawn at bin
    centres 0, 1, 2 ... use -0.5; heatmap cells spanning 0-1, 1-2 ... use 0.
    """
    positions = [first_edge_position + index * step
                 for index in range(len(bin_edges))]

    axis.set_xticks(positions)
    axis.set_xticklabels([str(edge) for edge in bin_edges], rotation=0)
    axis.set_xlim(positions[0], positions[-1])

def get_station_style(station_name: str) -> dict:
    """
    Returns:
        {"color", "marker", "linestyle", "hatch"} for the given station
    """
    style = STATION_STYLE_MAP.get(station_name)

    if style is None:
        return {"color": OVERALL_COLOR, "marker": "o", "linestyle": "-",
                "hatch": ""}

    return {
        "color": style["color"],
        "marker": style["marker"],
        "linestyle": style["linestyle"],
        "hatch": style["hatch"]
        }

def get_station_color(station_name: str) -> str:
    return get_station_style(station_name)["color"]

def get_station_colors(station_names: list[str]) -> list[str]:
    return [get_station_color(name) for name in station_names]
