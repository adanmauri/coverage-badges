"""Script para generar badges SVG de coverage.

Este script genera badges SVG de coverage que pueden ser importados
en README.md de otros proyectos de GitHub. Los badges se generan
con diferentes niveles de coverage y colores según el porcentaje.
"""

import argparse
from pathlib import Path


def get_color(coverage: float) -> str:
    """Determina el color del badge según el porcentaje de coverage.
    
    Args:
        coverage: Porcentaje de coverage (0-100).
        
    Returns:
        Color en formato hexadecimal.
    """
    if coverage >= 80:
        return "#4c1"
    elif coverage >= 60:
        return "#a3c51c"
    elif coverage >= 40:
        return "#dfb317"
    else:
        return "#e05d44"


def generate_svg(coverage: float, label: str = "coverage") -> str:
    """Genera el SVG del badge de coverage.
    
    Args:
        coverage: Porcentaje de coverage (0-100).
        label: Etiqueta del badge.
        
    Returns:
        Contenido SVG como string.
    """
    coverage_str = f"{coverage:.1f}%"
    color = get_color(coverage)
    
    # Calcular ancho del texto
    label_width = len(label) * 6 + 20
    message_width = len(coverage_str) * 6 + 20
    total_width = label_width + message_width
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{total_width}" height="20" role="img" aria-label="{label}: {coverage_str}">
  <title>{label}: {coverage_str}</title>
  <g shape-rendering="crispEdges">
    <rect width="{label_width}" height="20" fill="#555"/>
    <rect x="{label_width}" width="{message_width}" height="20" fill="{color}"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
    <text x="{label_width / 2}" y="15">{label}</text>
    <text x="{label_width + message_width / 2}" y="15">{coverage_str}</text>
  </g>
</svg>'''
    
    return svg


def main() -> None:
    """Función principal para generar badges."""
    parser = argparse.ArgumentParser(
        description="Generate coverage SVG badges"
    )
    parser.add_argument(
        "coverage",
        type=float,
        help="Coverage percentage (0-100)"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output file (default: badge.svg)"
    )
    parser.add_argument(
        "-l", "--label",
        type=str,
        default="coverage",
        help="Badge label (default: coverage)"
    )
    parser.add_argument(
        "-d", "--directory",
        type=str,
        default="badges",
        help="Directory to save the badge (default: badges)"
    )
    
    args = parser.parse_args()
    
    if not 0 <= args.coverage <= 100:
        print("Error: Coverage must be between 0 and 100")
        return
    
    # Crear directorio si no existe
    output_dir = Path(args.directory)
    output_dir.mkdir(exist_ok=True)
    
    # Determinar nombre del archivo
    if args.output:
        output_file = output_dir / args.output
    else:
        # Nombre basado en el coverage
        coverage_int = int(args.coverage)
        output_file = output_dir / f"coverage-{coverage_int}.svg"
    
    # Generar SVG
    svg_content = generate_svg(args.coverage, args.label)
    
    # Guardar archivo
    output_file.write_text(svg_content, encoding="utf-8")
    print(f"Badge generated: {output_file}")


if __name__ == "__main__":
    main()

