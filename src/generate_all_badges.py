"""Script para generar badges pre-hechos con diferentes niveles de coverage.

Genera badges SVG para niveles de coverage de 0% a 100% en incrementos
de 5%, para que puedan ser fácilmente importados en otros proyectos.
"""

import sys
from pathlib import Path

# Agregar el directorio padre al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generate_badge import generate_svg


def main() -> None:
    """Genera badges para todos los niveles de coverage."""
    badges_dir = Path("badges")
    badges_dir.mkdir(exist_ok=True)
    
    # Generar badges de 0% a 100% en incrementos de 5%
    for coverage in range(0, 101, 5):
        svg_content = generate_svg(float(coverage))
        output_file = badges_dir / f"coverage-{coverage}.svg"
        output_file.write_text(svg_content, encoding="utf-8")
        print(f"Generated: {output_file}")
    
    # También generar algunos valores específicos comunes
    for coverage in [25, 35, 45, 55, 65, 75, 85, 95]:
        if coverage % 5 != 0:  # Evitar duplicados
            svg_content = generate_svg(float(coverage))
            output_file = badges_dir / f"coverage-{coverage}.svg"
            output_file.write_text(svg_content, encoding="utf-8")
            print(f"Generated: {output_file}")
    
    print(f"\nTotal badges generated in {badges_dir}/")


if __name__ == "__main__":
    main()

