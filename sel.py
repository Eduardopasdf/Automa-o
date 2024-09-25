import webbrowser
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from collections import Counter

# Configuração do WebDriver
driver = webdriver.Chrome()
driver.get('https://www.zoom.com.br/')

wait = WebDriverWait(driver, 30)

# Tentar fechar o banner de política de privacidade
try:
    privacy_banner = wait.until(EC.visibility_of_element_located(
        (By.XPATH, "//div[contains(@class, 'PrivacyPolicy_PrivacyPolicy__nL9xT')]//button")))
    if privacy_banner.is_displayed():
        driver.execute_script("arguments[0].click();", privacy_banner)
except Exception as e:
    print(f"Banner de privacidade não encontrado ou não pode ser fechado. Erro: {e}")

# Rolando até o elemento para garantir que esteja visível
try:
    notebook_div = wait.until(EC.element_to_be_clickable((By.XPATH,
                                                          "//div[@class='Paper_Paper__4XALQ Paper_Paper__bordered__cl5Rh HotlinkCard_HotlinkCard__YfXNM' and .//p[text()='Notebook']]")))
    driver.execute_script("arguments[0].scrollIntoView();", notebook_div)
    driver.execute_script("arguments[0].click();", notebook_div)  # Tenta clicar no elemento
except Exception as e:
    print(f"Erro ao clicar no elemento Notebook: {e}")


# Função para verificar se a página terminou de carregar os notebooks
def wait_for_notebooks_to_load():
    try:
        wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "//h2[contains(@class, 'ProductCard_ProductCard_Name')]")))
    except Exception as e:
        print(f"Erro ao carregar os notebooks: {e}")


# Função para extrair os nomes dos notebooks na página atual
def get_notebook_names():
    wait_for_notebooks_to_load()  # Garantir que a página terminou de carregar
    try:
        notebook_elements = driver.find_elements(By.XPATH, "//h2[contains(@class, 'ProductCard_ProductCard_Name')]")
        notebook_names = [notebook.text for notebook in notebook_elements if notebook.text]  # Filtra nomes vazios
        if not notebook_names:
            print("Nenhum nome de notebook encontrado.")
        return notebook_names
    except Exception as e:
        print(f"Erro ao extrair nomes dos notebooks. Erro: {e}")
        return []


# Seleciona o filtro e retorna os notebooks
def get_notebooks_with_filter(filter_value):
    try:
        select_element = wait.until(EC.presence_of_element_located((By.ID, "orderBy")))
        select = Select(select_element)
        select.select_by_value(filter_value)
        print(f"Filtro '{filter_value}' aplicado.")

        return get_notebook_names()
    except Exception as e:
        print(f"Erro ao aplicar o filtro '{filter_value}'. Erro: {e}")
        return []


# Navega pelas páginas e coleta os notebooks
def coletar_notebooks_em_multiplas_paginas(filter_value, numero_paginas=3):
    all_notebooks = []

    # Aplica o filtro na página atual
    notebooks_atual = get_notebooks_with_filter(filter_value)
    all_notebooks.extend(notebooks_atual)

    # Navega pelas próximas páginas até o número limite definido (numero_paginas)
    for pagina in range(2, numero_paginas + 1):
        try:
            # Localiza e clica no link da próxima página (baseando no número da página)
            next_page_link = wait.until(EC.element_to_be_clickable(
                (By.XPATH, f"//a[@class='Paginator_pageLink__l_qQ6' and text()='{pagina}']")))
            driver.execute_script("arguments[0].click();", next_page_link)

            # Extrai os notebooks da nova página
            notebooks_atual = get_notebook_names()
            all_notebooks.extend(notebooks_atual)
        except Exception as e:
            print(f"Erro ao navegar para a página {pagina} ou não há mais páginas. Erro: {e}")
            break  # Sai do loop se não conseguir navegar

    return all_notebooks


# Gera uma lista HTML a partir dos notebooks encontrados
def gerar_lista_html(notebooks, titulo):
    html = f"<h3 class='text-center mt-4'>{titulo}</h3>\n"
    html += "<ul class='list-group list-group-flush mb-4'>\n"
    for notebook in notebooks:
        html += f"  <li class='list-group-item'>{notebook}</li>\n"
    html += "</ul>\n"
    return html


# Coleta os notebooks em múltiplas páginas para os três filtros
notebooks_melhor_avaliado = coletar_notebooks_em_multiplas_paginas("rating_desc", numero_paginas=3)  # Melhor avaliado
notebooks_menor_preco = coletar_notebooks_em_multiplas_paginas("price_asc", numero_paginas=3)  # Menor preço
notebooks_mais_relevante = coletar_notebooks_em_multiplas_paginas("lowering_percentage_desc",
                                                                  numero_paginas=3)  # Mais relevante

# Contabiliza a ocorrência de cada notebook nos três filtros
all_notebooks_combined = (
        notebooks_melhor_avaliado + notebooks_menor_preco + notebooks_mais_relevante
)
notebook_counts = Counter(all_notebooks_combined)

# Filtra apenas os notebooks que aparecem em todos os três filtros
notebooks_em_todos_filtros = [notebook for notebook, count in notebook_counts.items() if count >= 3]

# Seleciona os cinco melhores notebooks (se houver)
top_notebooks = notebooks_em_todos_filtros[:5]

# Gera listas HTML para os notebooks encontrados em todos os filtros e os cinco melhores
html_notebooks_melhor_avaliado = gerar_lista_html(notebooks_melhor_avaliado, "Notebooks mais bem avaliados:")
html_notebooks_menor_preco = gerar_lista_html(notebooks_menor_preco, "Notebooks com menor preço:")
html_notebooks_mais_relevante = gerar_lista_html(notebooks_mais_relevante, "Notebooks mais relevantes:")
html_top_notebooks = gerar_lista_html(top_notebooks, "Os 5 melhores notebooks que aparecem em todos os filtros:")

# Adiciona um cabeçalho do Bootstrap ao HTML
html_header = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>Notebooks Filtrados</title>
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="container">
    <div class="container mt-5">
        <h1 class="text-center">Lista de Notebooks Filtrados</h1>
        <hr>
"""

html_footer = """
    </div>
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.5.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# Combina o HTML gerado com cabeçalho e rodapé
html_final = html_header + html_notebooks_melhor_avaliado + html_notebooks_menor_preco + html_notebooks_mais_relevante + html_top_notebooks + html_footer

# Salva em arquivo HTML
file_path = "notebooks.html"
with open(file_path, "w", encoding="utf-8") as f:
    f.write(html_final)

# Exibe o HTML gerado
print(html_final)

# Fecha o navegador
driver.close()

# Abre o arquivo HTML no navegador padrão
webbrowser.open(file_path)
