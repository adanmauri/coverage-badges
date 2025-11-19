"""Badge generator module for coverage SVG badges.

This module provides a BadgeGenerator class that can generate
coverage SVG badges with different levels and colors.
"""

from pathlib import Path


class BadgeGenerator:
    """Generator for coverage SVG badges.

    This class provides methods to generate SVG badges for code coverage
    that can be imported in README.md files of GitHub projects.
    """

    def __init__(self) -> None:
        """Initialize the badge generator."""

    @staticmethod
    def get_color_gradient(coverage: float) -> tuple[str, str]:
        """Get gradient colors based on coverage percentage.

        Args:
            coverage: Coverage percentage (0-100).

        Returns:
            Tuple of (start_color, end_color) in hexadecimal format.
        """
        if coverage >= 80:
            return ("#34D058", "#28A745")  # Green gradient
        if coverage >= 60:
            return ("#A3C51C", "#8FA31C")  # Yellow-green gradient
        if coverage >= 40:
            return ("#DFB317", "#C99A00")  # Yellow gradient
        return ("#E05D44", "#C9302C")  # Red gradient

    @staticmethod
    def get_color(coverage: float) -> str:
        """Determine badge color based on coverage percentage.

        Args:
            coverage: Coverage percentage (0-100).

        Returns:
            Color in hexadecimal format.
        """
        if coverage >= 80:
            return "#4c1"
        if coverage >= 60:
            return "#a3c51c"
        if coverage >= 40:
            return "#dfb317"
        return "#e05d44"

    @staticmethod
    def _calculate_dimensions(label: str, coverage_str: str) -> dict[str, int]:
        """Calculate badge dimensions and positions.

        Args:
            label: Badge label text.
            coverage_str: Coverage percentage string.

        Returns:
            Dictionary with dimension values.
        """
        # Approximate character width: ~6.2px per character for DejaVu Sans 11px
        label_text_width = len(label) * 6.2
        message_text_width = len(coverage_str) * 6.2

        # Padding constants
        icon_x = 5
        icon_width_scaled = 14
        icon_margin = 4
        label_padding_left = icon_x + icon_width_scaled + icon_margin
        label_padding_right = 11
        message_padding_left = 4
        message_padding_right = 11

        label_width = int(label_text_width + label_padding_left + label_padding_right)
        message_width = int(message_text_width + message_padding_left + message_padding_right)
        total_width = label_width + message_width

        return {
            "label_width": label_width,
            "message_width": message_width,
            "total_width": total_width,
            "label_x": label_padding_left,
            "message_x": message_padding_left,
            "icon_x": icon_x,
        }

    def generate_svg(self, coverage: float, label: str = "Coverage") -> str:
        """Generate the coverage badge SVG.

        Args:
            coverage: Coverage percentage (0-100).
            label: Badge label text.

        Returns:
            SVG content as string.

        Raises:
            ValueError: If coverage is not between 0 and 100.
        """
        if not 0 <= coverage <= 100:
            raise ValueError("Coverage must be between 0 and 100")

        coverage_str = f"{coverage:.1f}%"
        start_color, end_color = self.get_color_gradient(coverage)
        dims = self._calculate_dimensions(label, coverage_str)

        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{dims["total_width"]}" height="20">\n'
            f"  <title>{label} - {coverage_str}</title>\n"
            f"  <defs>\n"
            f'    <linearGradient id="label-fill" x1="50%" y1="0%" x2="50%" y2="100%">\n'
            f'      <stop stop-color="#444D56" offset="0%"></stop>\n'
            f'      <stop stop-color="#24292E" offset="100%"></stop>\n'
            f"    </linearGradient>\n"
            f'    <linearGradient id="message-fill" x1="50%" y1="0%" x2="50%" y2="100%">\n'
            f'      <stop stop-color="{start_color}" offset="0%"></stop>\n'
            f'      <stop stop-color="{end_color}" offset="100%"></stop>\n'
            f"    </linearGradient>\n"
            f"  </defs>\n"
            f'  <g fill="none" fill-rule="evenodd">\n'
            f'    <g font-family="&#39;DejaVu Sans&#39;,Verdana,Geneva,sans-serif" '
            f'font-size="11">\n'
            f'      <path id="label-bg" '
            f'd="M0,3 C0,1.3431 1.3552,0 3.02702703,0 L{dims["label_width"]},0 '
            f"L{dims["label_width"]},20 L3.02702703,20 C1.3552,20 0,18.6569 0,17 "
            f'L0,3 Z" fill="url(#label-fill)" fill-rule="nonzero"></path>\n'
            f'      <text fill="#010101" fill-opacity=".3">\n'
            f'        <tspan x="{dims["label_x"]}" y="15" aria-hidden="true">{label}</tspan>\n'
            f"      </text>\n"
            f'      <text fill="#FFFFFF">\n'
            f'        <tspan x="{dims["label_x"]}" y="14">{label}</tspan>\n'
            f"      </text>\n"
            f"    </g>\n"
            f'    <g transform="translate({dims["label_width"]})" '
            f'font-family="&#39;DejaVu Sans&#39;,Verdana,Geneva,sans-serif" '
            f'font-size="11">\n'
            f'      <path d="M0 0h{dims["message_width"] - 3}C{dims["message_width"] - 1.061} 0 '
            f'{dims["message_width"]} 1.343 {dims["message_width"]} 3v14c0 1.657-1.37 3-3.061 '
            f'3H0V0z" id="message-bg" fill="url(#message-fill)" '
            f'fill-rule="nonzero"></path>\n'
            f'      <text fill="#010101" fill-opacity=".3" aria-hidden="true">\n'
            f'        <tspan x="{dims["message_x"]}" y="15">{coverage_str}</tspan>\n'
            f"      </text>\n"
            f'      <text fill="#FFFFFF">\n'
            f'        <tspan x="{dims["message_x"]}" y="14">{coverage_str}</tspan>\n'
            f"      </text>\n"
            f"    </g>\n"
            f'    <g transform="translate({dims["icon_x"]}, 3) scale(0.583)">\n'
            f'      <path fill="#959DA5" '
            f'd="M2.6152 0v.8867h3.8399V0zm5.0215 0v.8867h3.8418V0zm4.957 0v.8867h3.8418V0zm4.9356 '
            f"0v.8867h3.8418V0zM2.4473 1.8945a.935.935 0 0 0-.9356.9356c0 .517.4185.9375.9356.9375"
            f"h19.1054c.5171 0 .9356-.4204.9356-.9375a.935.935 0 0 0-.9356-.9356zm.168 2.8477V24"
            f"H6.455"
            f"V4.7422zm5.0214 0V20.543h3.8418V4.7422zm4.957 0V15.291h3.8497V4.7422zm4.9356 0v6.4941"
            f'h3.8418V4.7422z"></path>\n'
            f"    </g>\n"
            f"  </g>\n"
            f"</svg>"
        )

        return svg

    def generate_and_save_badge(
        self,
        coverage: float,
        output_path: Path,
        label: str = "Coverage",
    ) -> Path:
        """Generate a badge and save it to a file.

        Args:
            coverage: Coverage percentage (0-100).
            output_path: Path where to save the badge.
            label: Badge label text.

        Returns:
            Path to the saved badge.
        """
        svg_content = self.generate_svg(coverage, label)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(svg_content, encoding="utf-8")
        return output_path
