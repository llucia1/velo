"""
Scraper de categorías - jlwenti.com (Odoo)
==========================================
Genera /shared/categorias.csv con:
  - ID (nuestro, secuencial)
  - Active
  - Name (de og:title)
  - Parent category (nombre del padre)
  - Root category (1 si es nivel 1, 0 si no)
  - Image URL (construida con el ID de Odoo de la categoría)

Uso:
    python scraper_categorias.py

Variables de entorno opcionales:
    SUPPLIER_USER, SUPPLIER_PASS, SHARED_DIR
"""

import os
import re
import csv
import time
import logging
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

# ==============================================================================
# CONFIGURACIÓN
# ==============================================================================

BASE_URL      = "https://jlwenti.com"
LOGIN_URL     = f"{BASE_URL}/web/login"
SHARED_DIR    = os.environ.get("SHARED_DIR", "/shared")
SUPPLIER_USER = os.environ.get("SUPPLIER_USER", "bicis@bicicletadas.com")
SUPPLIER_PASS = os.environ.get("SUPPLIER_PASS", "Llucia-2018")
DELAY         = 0.8  # segundos entre peticiones

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9",
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# ==============================================================================
# LISTA COMPLETA DE SLUGS (416 categorías)
# ==============================================================================

SLUGS = [
    "/shop/category/bicicletas-455",
    "/shop/category/bicicletas-correpasillos-301",
    "/shop/category/bicicletas-12-pulgadas-89",
    "/shop/category/bicicletas-12-pulgadas-nino-90",
    "/shop/category/bicicletas-12-pulgadas-nina-91",
    "/shop/category/bicicletas-14-pulgadas-17",
    "/shop/category/bicicletas-14-pulgadas-nino-110",
    "/shop/category/bicicletas-14-pulgadas-nina-109",
    "/shop/category/bicicletas-16-pulgadas-6",
    "/shop/category/bicicletas-16-pulgadas-nino-8",
    "/shop/category/bicicletas-16-pulgadas-nina-7",
    "/shop/category/bicicletas-18-pulgadas-111",
    "/shop/category/bicicletas-18-pulgadas-nina-112",
    "/shop/category/bicicletas-18-pulgadas-nino-246",
    "/shop/category/bicicletas-20-pulgadas-10",
    "/shop/category/bicicletas-20-pulgadas-nino-13",
    "/shop/category/bicicletas-20-pulgadas-nina-11",
    "/shop/category/bicicletas-24-pulgadas-19",
    "/shop/category/bicicletas-24-pulgadas-hombre-252",
    "/shop/category/bicicletas-24-pulgadas-nina-20",
    "/shop/category/bicicletas-26-pulgadas-103",
    "/shop/category/bicicletas-26-pulgadas-aluminio-106",
    "/shop/category/bicicletas-26-pulgadas-aluminio-hombre-414",
    "/shop/category/bicicletas-26-pulgadas-aluminio-hombre-talla-15-416",
    "/shop/category/bicicletas-26-pulgadas-aluminio-hombre-talla-17-417",
    "/shop/category/bicicletas-26-pulgadas-aluminio-hombre-talla-18-418",
    "/shop/category/bicicletas-26-pulgadas-aluminio-hombre-talla-19-419",
    "/shop/category/bicicletas-26-pulgadas-aluminio-hombre-talla-20-420",
    "/shop/category/bicicletas-26-pulgadas-aluminio-hombre-talla-21-443",
    "/shop/category/bicicletas-26-pulgadas-aluminio-mujer-415",
    "/shop/category/bicicletas-26-pulgadas-aluminio-mujer-talla-15-421",
    "/shop/category/bicicletas-26-pulgadas-aluminio-mujer-talla-17-422",
    "/shop/category/bicicletas-26-pulgadas-aluminio-mujer-talla-18-423",
    "/shop/category/bicicletas-26-pulgadas-aluminio-mujer-talla-19-424",
    "/shop/category/bicicletas-26-pulgadas-hombre-107",
    "/shop/category/bicicletas-26-pulgadas-mujer-257",
    "/shop/category/bicicletas-26-pulgadas-paseo-cruiser-104",
    "/shop/category/bicicletas-27-5-pulgadas-437",
    "/shop/category/bicicletas-28-pulgadas-338",
    "/shop/category/bicicletas-29-pulgadas-438",
    "/shop/category/bicicletas-bmx-439",
    "/shop/category/bicicletas-e-bikes-502",
    "/shop/category/bicicletas-plegables-334",
    "/shop/category/bicicletas-oferta-488",
    "/shop/category/bicicletas-outlet-consultar-489",
    "/shop/category/accesorios-23",
    "/shop/category/accesorios-aros-de-pantalon-74",
    "/shop/category/accesorios-aletas-73",
    "/shop/category/accesorios-bidones-75",
    "/shop/category/accesorios-bidones-bidones-500-650-cc-76",
    "/shop/category/accesorios-bidones-bidones-700-1000-cc-78",
    "/shop/category/accesorios-bidones-bidones-infantiles-79",
    "/shop/category/accesorios-bidones-fundas-de-bidon-77",
    "/shop/category/accesorios-bolsos-80",
    "/shop/category/accesorios-bolsos-alforjas-81",
    "/shop/category/accesorios-bolsos-fundas-de-transporte-85",
    "/shop/category/accesorios-bolsos-fundas-movil-84",
    "/shop/category/accesorios-bolsos-bolsos-sillin-83",
    "/shop/category/accesorios-bolsos-mochilas-y-bolsas-hidratacion-82",
    "/shop/category/accesorios-candados-86",
    "/shop/category/accesorios-candados-candados-u-356",
    "/shop/category/accesorios-candados-varios-427",
    "/shop/category/accesorios-candados-100cm-429",
    "/shop/category/accesorios-candados-100cm-428",
    "/shop/category/accesorios-cestas-87",
    "/shop/category/accesorios-cestas-ctb-mtb-93",
    "/shop/category/accesorios-cestas-infantiles-88",
    "/shop/category/accesorios-cuentakilometros-99",
    "/shop/category/accesorios-cuentakilometros-smartwatch-516",
    "/shop/category/accesorios-cuentakilometros-varios-101",
    "/shop/category/accesorios-cuentakilometros-recambios-425",
    "/shop/category/accesorios-cuentakilometros-sigma-100",
    "/shop/category/accesorios-complementos-94",
    "/shop/category/accesorios-complementos-protectores-cuadro-96",
    "/shop/category/accesorios-complementos-tapones-de-valvula-97",
    "/shop/category/accesorios-complementos-adhesivos-95",
    "/shop/category/accesorios-complementos-varios-98",
    "/shop/category/accesorios-espejos-72",
    "/shop/category/accesorios-estabilizadores-113",
    "/shop/category/accesorios-estabilizadores-recambios-115",
    "/shop/category/accesorios-estabilizadores-estabilizadores-114",
    "/shop/category/accesorios-expositores-y-perchas-133",
    "/shop/category/accesorios-expositores-y-perchas-expositores-116",
    "/shop/category/accesorios-expositores-y-perchas-perchas-132",
    "/shop/category/accesorios-guardabarros-117",
    "/shop/category/accesorios-infladores-26",
    "/shop/category/accesorios-infladores-accesorios-infladores-27",
    "/shop/category/accesorios-infladores-accesorios-infladores-abrazaderas-123",
    "/shop/category/accesorios-infladores-accesorios-infladores-adaptadores-28",
    "/shop/category/accesorios-infladores-accesorios-infladores-racord-118",
    "/shop/category/accesorios-infladores-accesorios-infladores-bombonas-co2-121",
    "/shop/category/accesorios-infladores-clasicas-122",
    "/shop/category/accesorios-infladores-infladores-taller-120",
    "/shop/category/accesorios-infladores-mini-infladores-58",
    "/shop/category/accesorios-luces-55",
    "/shop/category/accesorios-luces-recambios-y-baterias-446",
    "/shop/category/accesorios-luces-trasera-129",
    "/shop/category/accesorios-luces-conjuntos-56",
    "/shop/category/accesorios-luces-dinamo-124",
    "/shop/category/accesorios-luces-reflectores-128",
    "/shop/category/accesorios-luces-delantera-57",
    "/shop/category/accesorios-patas-131",
    "/shop/category/accesorios-portabidones-24",
    "/shop/category/accesorios-portabidones-acero-134",
    "/shop/category/accesorios-portabidones-aluminio-25",
    "/shop/category/accesorios-portabidones-fibra-137",
    "/shop/category/accesorios-portabidones-carbono-135",
    "/shop/category/accesorios-portabidones-varios-139",
    "/shop/category/accesorios-portabidones-infantil-138",
    "/shop/category/accesorios-portabultos-140",
    "/shop/category/accesorios-portabultos-pulpos-142",
    "/shop/category/accesorios-portabultos-trasero-143",
    "/shop/category/accesorios-portabultos-a-la-tija-144",
    "/shop/category/accesorios-portabultos-delantera-141",
    "/shop/category/accesorios-posapies-145",
    "/shop/category/accesorios-protesis-31",
    "/shop/category/accesorios-sillitas-portabebes-149",
    "/shop/category/accesorios-sillitas-portabebes-portamunecas-152",
    "/shop/category/accesorios-sillitas-portabebes-al-portamaletas-153",
    "/shop/category/accesorios-sillitas-portabebes-delantera-151",
    "/shop/category/accesorios-sillitas-portabebes-al-cuadro-150",
    "/shop/category/accesorios-timbres-29",
    "/shop/category/accesorios-timbres-bocinas-347",
    "/shop/category/accesorios-timbres-expositores-484",
    "/shop/category/accesorios-timbres-adulto-154",
    "/shop/category/accesorios-timbres-infantil-30",
    "/shop/category/componentes-452",
    "/shop/category/componentes-bielas-156",
    "/shop/category/componentes-bielas-bielas-acero-158",
    "/shop/category/componentes-bielas-bielas-aluminio-157",
    "/shop/category/componentes-bielas-bielas-bmx-426",
    "/shop/category/componentes-bielas-bielas-e-bike-523",
    "/shop/category/componentes-bolas-y-rodamientos-159",
    "/shop/category/componentes-bolas-y-rodamientos-bolas-483",
    "/shop/category/componentes-bolas-y-rodamientos-direccion-161",
    "/shop/category/componentes-bolas-y-rodamientos-pedalier-162",
    "/shop/category/componentes-bolas-y-rodamientos-rueda-163",
    "/shop/category/componentes-bolas-y-rodamientos-sellados-493",
    "/shop/category/componentes-cables-guias-terminales-48",
    "/shop/category/componentes-cables-guias-terminales-cambio-165",
    "/shop/category/componentes-cables-guias-terminales-freno-166",
    "/shop/category/componentes-cables-guias-terminales-terminales-450",
    "/shop/category/componentes-cables-guias-terminales-terminales-y-guias-164",
    "/shop/category/componentes-camaras-52",
    "/shop/category/componentes-camaras-12-366",
    "/shop/category/componentes-camaras-14-367",
    "/shop/category/componentes-camaras-16-368",
    "/shop/category/componentes-camaras-18-369",
    "/shop/category/componentes-camaras-20-370",
    "/shop/category/componentes-camaras-24-371",
    "/shop/category/componentes-camaras-26-372",
    "/shop/category/componentes-camaras-27-5-373",
    "/shop/category/componentes-camaras-28-449",
    "/shop/category/componentes-camaras-29-375",
    "/shop/category/componentes-camaras-700-374",
    "/shop/category/componentes-camaras-otras-444",
    "/shop/category/componentes-cadenas-167",
    "/shop/category/componentes-cadenas-recambios-170",
    "/shop/category/componentes-cadenas-rollos-de-cadena-336",
    "/shop/category/componentes-cadenas-1-vel-168",
    "/shop/category/componentes-cadenas-5-6-7-8-vel-169",
    "/shop/category/componentes-cadenas-9-10-vel-514",
    "/shop/category/componentes-cadenas-11-12-vel-495",
    "/shop/category/componentes-cambios-69",
    "/shop/category/componentes-cambios-mandos-de-cambio-70",
    "/shop/category/componentes-cambios-cambios-traseros-174",
    "/shop/category/componentes-cambios-desviadores-36",
    "/shop/category/componentes-cambios-protector-de-cambio-171",
    "/shop/category/componentes-cambios-recambios-173",
    "/shop/category/componentes-camisas-176",
    "/shop/category/componentes-camisas-accesorios-177",
    "/shop/category/componentes-camisas-cambio-178",
    "/shop/category/componentes-camisas-freno-179",
    "/shop/category/componentes-pinones-46",
    "/shop/category/componentes-pinones-fijos-482",
    "/shop/category/componentes-pinones-1-velocidad-283",
    "/shop/category/componentes-pinones-cassette-284",
    "/shop/category/componentes-pinones-rosca-47",
    "/shop/category/componentes-cierres-180",
    "/shop/category/componentes-cierres-conjuntos-182",
    "/shop/category/componentes-cierres-rueda-183",
    "/shop/category/componentes-cierres-sillin-181",
    "/shop/category/componentes-cierres-pasante-518",
    "/shop/category/componentes-cintas-de-manillar-185",
    "/shop/category/componentes-cubiertas-272",
    "/shop/category/componentes-cubiertas-otras-307",
    "/shop/category/componentes-cubiertas-12-274",
    "/shop/category/componentes-cubiertas-14-275",
    "/shop/category/componentes-cubiertas-16-276",
    "/shop/category/componentes-cubiertas-18-277",
    "/shop/category/componentes-cubiertas-20-278",
    "/shop/category/componentes-cubiertas-22-353",
    "/shop/category/componentes-cubiertas-24-279",
    "/shop/category/componentes-cubiertas-26-280",
    "/shop/category/componentes-cubiertas-26-26x1-75-435",
    "/shop/category/componentes-cubiertas-26-26x1-75-436",
    "/shop/category/componentes-cubiertas-26-26x1-3-8-varias-434",
    "/shop/category/componentes-cubiertas-27-5-335",
    "/shop/category/componentes-cubiertas-28-700-281",
    "/shop/category/componentes-cubiertas-28-700-ctb-431",
    "/shop/category/componentes-cubiertas-28-700-road-432",
    "/shop/category/componentes-cubiertas-29-282",
    "/shop/category/componentes-direcciones-62",
    "/shop/category/componentes-direcciones-ahead-187",
    "/shop/category/componentes-direcciones-rosca-188",
    "/shop/category/componentes-direcciones-varios-64",
    "/shop/category/componentes-direcciones-espaciadores-63",
    "/shop/category/componentes-ejes-pedalier-189",
    "/shop/category/componentes-ejes-pedalier-cazoletas-190",
    "/shop/category/componentes-ejes-pedalier-pedalier-sellado-191",
    "/shop/category/componentes-ejes-pedalier-recambios-192",
    "/shop/category/componentes-ejes-pedalier-simple-193",
    "/shop/category/componentes-frenos-50",
    "/shop/category/componentes-frenos-adaptadores-de-disco-471",
    "/shop/category/componentes-frenos-cantilever-196",
    "/shop/category/componentes-frenos-carretera-197",
    "/shop/category/componentes-frenos-discos-198",
    "/shop/category/componentes-frenos-frenos-varilla-477",
    "/shop/category/componentes-frenos-herradura-195",
    "/shop/category/componentes-frenos-pastillas-de-disco-200",
    "/shop/category/componentes-frenos-pastillas-de-disco-alligator-448",
    "/shop/category/componentes-frenos-pastillas-de-disco-avid-398",
    "/shop/category/componentes-frenos-pastillas-de-disco-cannondale-403",
    "/shop/category/componentes-frenos-pastillas-de-disco-diatech-407",
    "/shop/category/componentes-frenos-pastillas-de-disco-formula-399",
    "/shop/category/componentes-frenos-pastillas-de-disco-fsa-413",
    "/shop/category/componentes-frenos-pastillas-de-disco-giant-404",
    "/shop/category/componentes-frenos-pastillas-de-disco-hayes-401",
    "/shop/category/componentes-frenos-pastillas-de-disco-hope-402",
    "/shop/category/componentes-frenos-pastillas-de-disco-joytech-412",
    "/shop/category/componentes-frenos-pastillas-de-disco-mangura-406",
    "/shop/category/componentes-frenos-pastillas-de-disco-promax-408",
    "/shop/category/componentes-frenos-pastillas-de-disco-quad-442",
    "/shop/category/componentes-frenos-pastillas-de-disco-rst-410",
    "/shop/category/componentes-frenos-pastillas-de-disco-shimano-397",
    "/shop/category/componentes-frenos-pastillas-de-disco-sram-411",
    "/shop/category/componentes-frenos-pastillas-de-disco-suntour-405",
    "/shop/category/componentes-frenos-pastillas-de-disco-tektro-400",
    "/shop/category/componentes-frenos-pastillas-de-disco-trp-409",
    "/shop/category/componentes-frenos-pastillas-de-disco-varias-496",
    "/shop/category/componentes-frenos-pastillas-de-disco-zoom-441",
    "/shop/category/componentes-frenos-pinzas-de-disco-199",
    "/shop/category/componentes-frenos-v-brake-53",
    "/shop/category/componentes-frenos-zapatas-71",
    "/shop/category/componentes-frenos-zapatas-cantilever-361",
    "/shop/category/componentes-frenos-zapatas-carretera-364",
    "/shop/category/componentes-frenos-zapatas-tipo-antiguo-363",
    "/shop/category/componentes-frenos-zapatas-v-brake-362",
    "/shop/category/componentes-frenos-manetas-54",
    "/shop/category/componentes-frenos-recambios-51",
    "/shop/category/componentes-frenos-recambios-curvas-v-brake-472",
    "/shop/category/componentes-frenos-recambios-frenos-hidraulicos-473",
    "/shop/category/componentes-frenos-recambios-gomas-v-brake-476",
    "/shop/category/componentes-frenos-recambios-perchas-de-freno-474",
    "/shop/category/componentes-frenos-recambios-prisionero-y-otros-478",
    "/shop/category/componentes-frenos-recambios-tensores-475",
    "/shop/category/componentes-horquillas-4",
    "/shop/category/componentes-horquillas-16-203",
    "/shop/category/componentes-horquillas-18-204",
    "/shop/category/componentes-horquillas-20-201",
    "/shop/category/componentes-horquillas-24-202",
    "/shop/category/componentes-horquillas-26-205",
    "/shop/category/componentes-horquillas-27-5-348",
    "/shop/category/componentes-horquillas-28-206",
    "/shop/category/componentes-horquillas-29-349",
    "/shop/category/componentes-horquillas-accesorios-207",
    "/shop/category/componentes-manillares-208",
    "/shop/category/componentes-manillares-adaptadores-481",
    "/shop/category/componentes-manillares-bmx-211",
    "/shop/category/componentes-manillares-ctb-212",
    "/shop/category/componentes-manillares-mtb-214",
    "/shop/category/componentes-manillares-carretera-gravel-515",
    "/shop/category/componentes-partes-cuadro-37",
    "/shop/category/componentes-partes-cuadro-suspension-cuadro-215",
    "/shop/category/componentes-partes-cuadro-varios-355",
    "/shop/category/componentes-partes-cuadro-patillas-cuadro-38",
    "/shop/category/componentes-pedales-59",
    "/shop/category/componentes-pedales-automaticos-216",
    "/shop/category/componentes-pedales-calas-219",
    "/shop/category/componentes-pedales-ciclostatic-220",
    "/shop/category/componentes-pedales-ctb-222",
    "/shop/category/componentes-pedales-infantiles-453",
    "/shop/category/componentes-pedales-plegables-454",
    "/shop/category/componentes-pedales-bmx-218",
    "/shop/category/componentes-pedales-rastrales-223",
    "/shop/category/componentes-pedales-mtb-60",
    "/shop/category/componentes-platos-43",
    "/shop/category/componentes-platos-sueltos-494",
    "/shop/category/componentes-platos-bmx-225",
    "/shop/category/componentes-platos-un-plato-229",
    "/shop/category/componentes-platos-doble-plato-228",
    "/shop/category/componentes-platos-e-bike-517",
    "/shop/category/componentes-platos-triple-plato-227",
    "/shop/category/componentes-platos-protector-plato-45",
    "/shop/category/componentes-platos-recambios-44",
    "/shop/category/componentes-potencias-39",
    "/shop/category/componentes-potencias-prolongadores-231",
    "/shop/category/componentes-potencias-tornillos-y-lanas-232",
    "/shop/category/componentes-potencias-cana-potencia-40",
    "/shop/category/componentes-potencias-ahead-66",
    "/shop/category/componentes-punos-233",
    "/shop/category/componentes-punos-bmx-386",
    "/shop/category/componentes-punos-ctb-387",
    "/shop/category/componentes-punos-mtb-236",
    "/shop/category/componentes-punos-mtb-espuma-foam-388",
    "/shop/category/componentes-punos-mtb-goma-gel-389",
    "/shop/category/componentes-punos-infantiles-234",
    "/shop/category/componentes-ruedas-componentes-41",
    "/shop/category/componentes-ruedas-componentes-llantas-492",
    "/shop/category/componentes-ruedas-componentes-protector-de-radios-240",
    "/shop/category/componentes-ruedas-componentes-radios-241",
    "/shop/category/componentes-ruedas-componentes-ruedas-completas-243",
    "/shop/category/componentes-ruedas-componentes-ruedas-completas-12-376",
    "/shop/category/componentes-ruedas-componentes-ruedas-completas-14-377",
    "/shop/category/componentes-ruedas-componentes-ruedas-completas-16-378",
    "/shop/category/componentes-ruedas-componentes-ruedas-completas-18-379",
    "/shop/category/componentes-ruedas-componentes-ruedas-completas-20-380",
    "/shop/category/componentes-ruedas-componentes-ruedas-completas-20-bmx-459",
    "/shop/category/componentes-ruedas-componentes-ruedas-completas-20-mtb-458",
    "/shop/category/componentes-ruedas-componentes-ruedas-completas-24-381",
    "/shop/category/componentes-ruedas-componentes-ruedas-completas-26-382",
    "/shop/category/componentes-ruedas-componentes-ruedas-completas-26-disco-456",
    "/shop/category/componentes-ruedas-componentes-ruedas-completas-26-v-brake-457",
    "/shop/category/componentes-ruedas-componentes-ruedas-completas-27-5-383",
    "/shop/category/componentes-ruedas-componentes-ruedas-completas-29-385",
    "/shop/category/componentes-ruedas-componentes-ruedas-completas-700-384",
    "/shop/category/componentes-ruedas-componentes-tuercas-242",
    "/shop/category/componentes-ruedas-componentes-bujes-237",
    "/shop/category/componentes-ruedas-componentes-ejes-de-rueda-238",
    "/shop/category/componentes-ruedas-componentes-valvulas-244",
    "/shop/category/componentes-ruedas-componentes-fondos-de-llanta-42",
    "/shop/category/componentes-sillines-67",
    "/shop/category/componentes-sillines-ctb-498",
    "/shop/category/componentes-sillines-infantiles-265",
    "/shop/category/componentes-sillines-bmx-263",
    "/shop/category/componentes-sillines-cadete-487",
    "/shop/category/componentes-sillines-mtb-126",
    "/shop/category/componentes-sillines-elastomeros-264",
    "/shop/category/componentes-sillines-con-muelles-68",
    "/shop/category/componentes-sillines-ciclostatic-351",
    "/shop/category/componentes-sillines-nuez-de-sillin-266",
    "/shop/category/componentes-sillines-fundas-de-sillin-267",
    "/shop/category/componentes-tijas-de-sillin-268",
    "/shop/category/componentes-tijas-de-sillin-tija-270",
    "/shop/category/componentes-tijas-de-sillin-tubo-269",
    "/shop/category/componentes-tijas-de-sillin-telescopica-500",
    "/shop/category/moto-304",
    "/shop/category/moto-adhesivos-352",
    "/shop/category/moto-prisioneros-318",
    "/shop/category/moto-punos-310",
    "/shop/category/moto-tubos-de-gasolina-305",
    "/shop/category/moto-varios-306",
    "/shop/category/taller-32",
    "/shop/category/taller-banco-de-taller-273",
    "/shop/category/taller-mantenimiento-bicicleta-341",
    "/shop/category/taller-mantenimiento-bicicleta-antipinchazos-342",
    "/shop/category/taller-mantenimiento-bicicleta-grasas-344",
    "/shop/category/taller-mantenimiento-bicicleta-limpiadores-343",
    "/shop/category/taller-mantenimiento-bicicleta-lubricantes-345",
    "/shop/category/taller-mantenimiento-bicicleta-otros-346",
    "/shop/category/taller-herramientas-33",
    "/shop/category/taller-herramientas-desmontables-34",
    "/shop/category/taller-herramientas-extractores-285",
    "/shop/category/taller-herramientas-kit-herramientas-340",
    "/shop/category/taller-herramientas-llave-pedalier-339",
    "/shop/category/taller-herramientas-tornilleria-292",
    "/shop/category/taller-herramientas-tronchacadenas-289",
    "/shop/category/taller-herramientas-llave-de-cadena-286",
    "/shop/category/taller-herramientas-llave-pinon-287",
    "/shop/category/taller-herramientas-llave-radios-288",
    "/shop/category/taller-herramientas-parches-291",
    "/shop/category/taller-herramientas-torque-490",
    "/shop/category/taller-herramientas-varios-61",
    "/shop/category/ropa-y-protecciones-451",
    "/shop/category/ropa-y-protecciones-botines-y-calcetines-312",
    "/shop/category/ropa-y-protecciones-gafas-491",
    "/shop/category/ropa-y-protecciones-protecciones-337",
    "/shop/category/ropa-y-protecciones-zapatillas-499",
    "/shop/category/ropa-y-protecciones-cascos-308",
    "/shop/category/ropa-y-protecciones-cascos-adulto-309",
    "/shop/category/ropa-y-protecciones-cascos-infantiles-317",
    "/shop/category/ropa-y-protecciones-impermeable-313",
    "/shop/category/ropa-y-protecciones-invierno-314",
    "/shop/category/ropa-y-protecciones-verano-315",
    "/shop/category/ropa-y-protecciones-guantes-319",
    "/shop/category/ropa-y-protecciones-guantes-adulto-321",
    "/shop/category/ropa-y-protecciones-guantes-invierno-460",
    "/shop/category/ropa-y-protecciones-guantes-infantiles-320",
    "/shop/category/otros-1",
    "/shop/category/otros-carritos-293",
    "/shop/category/otros-portabicicletas-295",
    "/shop/category/otros-portabicicletas-accesorios-296",
    "/shop/category/otros-portabicicletas-techo-297",
    "/shop/category/otros-portabicicletas-trasero-298",
    "/shop/category/otros-rodillos-299",
    "/shop/category/otros-scooter-300",
    "/shop/category/otros-ciclostatic-spinning-302",
    "/shop/category/patinete-506",
    "/shop/category/patinete-cubiertas-508",
    "/shop/category/patinete-camaras-521",
    "/shop/category/patinete-ruedas-y-despieze-522",
    "/shop/category/patinete-chasis-y-partes-519",
    "/shop/category/patinete-cableado-520",
    "/shop/category/patinete-luces-512",
    "/shop/category/patinete-electrico-509",
    "/shop/category/patinete-frenos-507",
    "/shop/category/patinete-varios-510",
    "/shop/category/fixie-bike-359",
    "/shop/category/recambios-ebikes-525",
    "/shop/category/recambios-ebikes-centralitas-526",
    "/shop/category/recambios-ebikes-luces-531",
    "/shop/category/recambios-ebikes-varios-530",
    "/shop/category/recambios-ebikes-conexiones-527",
    "/shop/category/recambios-ebikes-sensores-528",
    "/shop/category/recambios-ebikes-display-529",
    "/shop/category/fat-bike-357",
]

# Categorías de nivel 1 (sin padre, root=1)
ROOT_SLUGS = {
    "/shop/category/bicicletas-455",
    "/shop/category/accesorios-23",
    "/shop/category/componentes-452",
    "/shop/category/moto-304",
    "/shop/category/taller-32",
    "/shop/category/ropa-y-protecciones-451",
    "/shop/category/otros-1",
    "/shop/category/patinete-506",
    "/shop/category/fixie-bike-359",
    "/shop/category/recambios-ebikes-525",
    "/shop/category/fat-bike-357",
}

# ==============================================================================
# HELPERS
# ==============================================================================

def get_odoo_id(slug: str) -> str:
    """Extrae el ID numérico al final del slug"""
    parts = slug.rsplit('-', 1)
    if len(parts) == 2 and parts[1].isdigit():
        return parts[1]
    return ''


def slug_without_id(slug: str) -> str:
    parts = slug.rsplit('-', 1)
    if len(parts) == 2 and parts[1].isdigit():
        return parts[0]
    return slug


def find_parent_slug(current_slug: str, all_no_id: list) -> str | None:
    current_no_id = slug_without_id(current_slug)
    best = None
    best_len = 0
    for s in all_no_id:
        if s != current_no_id and current_no_id.startswith(s + '-'):
            if len(s) > best_len:
                best = s
                best_len = len(s)
    return best

def clean_prestashop_category_name(name: str) -> str:
    """Limpia nombres de categoría para que PrestaShop los acepte."""
    name = (name or '').strip()

    # Casos típicos de medidas/rangos del proveedor
    name = re.sub(r'^>\s*(.+)$', r'Mayor que \1', name)
    name = re.sub(r'^<\s*(.+)$', r'Menor que \1', name)

    # Caracteres que PrestaShop no permite en Category->name
    name = name.replace('>', ' mayor que ')
    name = name.replace('<', ' menor que ')
    name = name.replace('{', '(')
    name = name.replace('}', ')')

    # Normalizar espacios
    name = ' '.join(name.split())

    return name

# ==============================================================================
# LOGIN
# ==============================================================================

def login(session: requests.Session) -> bool:
    log.info("Haciendo login...")
    r = session.get(LOGIN_URL, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(r.text, 'lxml')
    csrf = soup.find('input', {'name': 'csrf_token'})
    if not csrf:
        log.error("csrf_token no encontrado")
        return False

    r = session.post(LOGIN_URL, data={
        'login':      SUPPLIER_USER,
        'password':   SUPPLIER_PASS,
        'csrf_token': csrf['value'],
        'redirect':   '/shop',
    }, headers={**HEADERS, 'Referer': LOGIN_URL}, timeout=30, allow_redirects=True)

    if '/web/login' in r.url:
        log.error("Login fallido")
        return False

    log.info(f"Login OK")
    return True


# ==============================================================================
# SCRAPING DE UNA CATEGORÍA
# ==============================================================================

def scrape_category(session: requests.Session, slug: str) -> dict:
    url = BASE_URL + slug
    odoo_id = get_odoo_id(slug)

    result = {
        'slug':      slug,
        'odoo_id':   odoo_id,
        'name':      '',
        'image_url': f"{BASE_URL}/website/image?model=product.public.category&id={odoo_id}&field=image_512" if odoo_id else '',
    }

    try:
        r = session.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'lxml')

        # Nombre desde og:title -> "Nombre | My Website"
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            result['name'] = og_title['content'].split('|')[0].strip()

        # Fallback: title tag
        if not result['name']:
            title = soup.find('title')
            if title:
                result['name'] = title.get_text().split('|')[0].strip()

    except Exception as e:
        log.warning(f"Error en {url}: {e}")

    return result
def make_link_rewrite(slug: str, odoo_id: str) -> str:
    """
    Genera una URL amigable válida para PrestaShop usando el slug del proveedor.
    No usa el nombre de la categoría porque puede contener caracteres como >.
    """
    clean = slug.strip('/')

    if clean.startswith('shop/category/'):
        clean = clean[len('shop/category/'):]

    clean = slug_without_id(clean)

    clean = clean.lower()
    clean = re.sub(r'[^a-z0-9-]+', '-', clean)
    clean = re.sub(r'-+', '-', clean)
    clean = clean.strip('-')

    if odoo_id:
        clean = f"{clean}-{odoo_id}"

    return clean or f"categoria-{odoo_id}"

def make_link_rewrite(name: str, slug: str, ps_id: int) -> str:
    """
    Genera una URL amigable válida para PrestaShop.

    Usa el nombre para respetar mayor-que / menor-que.
    Añade nuestro ID de PrestaShop al final para evitar duplicados.
    """
    raw_name = (name or '').strip()
    clean_name = raw_name.lower()

    if raw_name.startswith('>'):
        base = 'mayor-que-' + raw_name[1:].strip()
    elif raw_name.startswith('<'):
        base = 'menor-que-' + raw_name[1:].strip()
    elif clean_name.startswith('mayor que '):
        base = raw_name
    elif clean_name.startswith('menor que '):
        base = raw_name
    else:
        base = (slug or '').strip('/')

        if base.startswith('shop/category/'):
            base = base[len('shop/category/'):]

        base = slug_without_id(base)

    base = base.lower()

    base = (
        base
        .replace('á', 'a')
        .replace('é', 'e')
        .replace('í', 'i')
        .replace('ó', 'o')
        .replace('ú', 'u')
        .replace('ü', 'u')
        .replace('ñ', 'n')
    )

    base = re.sub(r'[^a-z0-9]+', '-', base)
    base = re.sub(r'-+', '-', base)
    base = base.strip('-')

    return f"{base}" if base else f"categoria-{ps_id}"


# ==============================================================================
# MAIN
# ==============================================================================

def main():
    os.makedirs(SHARED_DIR, exist_ok=True)

    session = requests.Session()
    session.headers.update(HEADERS)

    if not login(session):
        log.error("Abortando")
        return

    # Construir mapa de padres
    all_no_id = [slug_without_id(s) for s in SLUGS]
    no_id_to_slug = {slug_without_id(s): s for s in SLUGS}

    # Scraping
    results = []
    total = len(SLUGS)
    for i, slug in enumerate(SLUGS, 1):
        log.info(f"[{i}/{total}] {slug}")
        data = scrape_category(session, slug)

        # Padre
        parent_no_id = find_parent_slug(slug, all_no_id)
        if parent_no_id:
            parent_slug = no_id_to_slug.get(parent_no_id, '')
            # El nombre del padre lo tendremos después - usamos slug por ahora
            data['parent_slug'] = parent_slug
            data['is_root'] = 0
        else:
            data['parent_slug'] = ''
            data['is_root'] = 1

        results.append(data)
        time.sleep(DELAY)

    # IDs propios desde 100 para evitar colisiones con PS (Home=1, Root=2)
    ID_START = 100
    slug_to_ps_id = {r['slug']: ID_START + i for i, r in enumerate(results)}

    # Generar CSV
    csv_path = os.path.join(SHARED_DIR, 'categorias.csv')
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow([
            'Category ID', 'Active (0/1)', 'Name *',
            'Parent category', 'Root category (0/1)',
            'Description', 'Meta title', 'Meta description',
            'URL rewritten', 'Image URL'
        ])
        for r in results:
            ps_id = slug_to_ps_id[r['slug']]
            if r['parent_slug'] and r['parent_slug'] in slug_to_ps_id:
                parent_id = slug_to_ps_id[r['parent_slug']]
            else:
                parent_id = 1  # Home en PrestaShop
            writer.writerow([
                ps_id,
                1,
                clean_prestashop_category_name(r['name']),
                parent_id,
                r['is_root'],
                '',
                '',
                '',
                make_link_rewrite(r['name'], r['slug'], ps_id),
                r['image_url'],
            ])

    log.info(f"=== DONE: {csv_path} ({len(results)} categorías) ===")


if __name__ == '__main__':
    main()
