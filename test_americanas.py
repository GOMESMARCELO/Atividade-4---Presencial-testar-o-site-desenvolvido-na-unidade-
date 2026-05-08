"""
Teste Automatizado de Navegabilidade - Americanas.com.br
Utiliza Selenium WebDriver com Chrome em modo headless.

Requisitos:
    pip install selenium webdriver-manager

Execução:
    python test_americanas.py
"""

import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


# ──────────────────────────────────────────────
# Configurações globais
# ──────────────────────────────────────────────
BASE_URL = "https://www.americanas.com.br"
TIMEOUT  = 15          # segundos de espera máxima por elemento
HEADLESS = True        # False → abre o browser visível (útil para depurar)


def build_driver() -> webdriver.Chrome:
    """Cria e retorna um WebDriver configurado."""
    options = Options()
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


# ──────────────────────────────────────────────
# Classe base
# ──────────────────────────────────────────────
class AmericanasBaseTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.driver = build_driver()
        cls.wait   = WebDriverWait(cls.driver, TIMEOUT)
        cls.driver.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    # ── Helpers ──────────────────────────────
    def _go(self, path: str = ""):
        self.driver.get(BASE_URL + path)

    def _wait_url_contains(self, text: str, timeout: int = TIMEOUT):
        WebDriverWait(self.driver, timeout).until(EC.url_contains(text))

    def _find(self, by, value):
        return self.wait.until(EC.presence_of_element_located((by, value)))

    def _click(self, by, value):
        el = self.wait.until(EC.element_to_be_clickable((by, value)))
        self.driver.execute_script("arguments[0].scrollIntoView(true);", el)
        el.click()
        return el

    def _screenshot(self, name: str):
        path = f"screenshot_{name}.png"
        self.driver.save_screenshot(path)
        print(f"  📸 Screenshot salvo: {path}")


# ──────────────────────────────────────────────
# TC-01 · Homepage carrega corretamente
# ──────────────────────────────────────────────
class TC01_Homepage(AmericanasBaseTest):

    def test_01_titulo_da_pagina(self):
        """A homepage deve conter 'Americanas' no título."""
        self._go()
        self.assertIn("Americanas", self.driver.title)
        print(f"  ✅ Título: {self.driver.title}")

    def test_02_logo_visivel(self):
        """O logo da Americanas deve estar presente no DOM."""
        self._go()
        # Tenta localizar via tag <a> com href raiz ou imagem de logo
        selectors = [
            (By.CSS_SELECTOR, "a[href='/']"),
            (By.CSS_SELECTOR, "img[alt*='americanas' i]"),
            (By.CSS_SELECTOR, "[class*='logo' i]"),
        ]
        found = False
        for by, value in selectors:
            try:
                self.driver.find_element(by, value)
                found = True
                break
            except NoSuchElementException:
                continue
        self.assertTrue(found, "Logo / link home não encontrado na homepage.")
        print("  ✅ Logo/home link encontrado.")

    def test_03_status_http_200(self):
        """Verifica que a página carregou sem erro (URL mantida)."""
        self._go()
        self.assertIn("americanas", self.driver.current_url)
        print(f"  ✅ URL atual: {self.driver.current_url}")


# ──────────────────────────────────────────────
# TC-02 · Barra de busca
# ──────────────────────────────────────────────
class TC02_Busca(AmericanasBaseTest):

    TERMO = "notebook"

    def test_01_campo_de_busca_presente(self):
        """Campo de busca deve existir na homepage."""
        self._go()
        selectors = [
            (By.CSS_SELECTOR, "input[placeholder*='busca' i]"),
            (By.CSS_SELECTOR, "input[placeholder*='pesquisa' i]"),
            (By.CSS_SELECTOR, "input[type='search']"),
            (By.NAME, "q"),
        ]
        campo = None
        for by, value in selectors:
            try:
                campo = self.driver.find_element(by, value)
                break
            except NoSuchElementException:
                continue
        self.assertIsNotNone(campo, "Campo de busca não encontrado.")
        print("  ✅ Campo de busca presente.")

    def test_02_busca_retorna_resultados(self):
        """Buscar por 'notebook' deve exibir resultados."""
        self._go()
        selectors = [
            (By.CSS_SELECTOR, "input[placeholder*='busca' i]"),
            (By.CSS_SELECTOR, "input[placeholder*='pesquisa' i]"),
            (By.CSS_SELECTOR, "input[type='search']"),
            (By.NAME, "q"),
        ]
        campo = None
        for by, value in selectors:
            try:
                campo = self.driver.find_element(by, value)
                break
            except NoSuchElementException:
                continue
        self.assertIsNotNone(campo, "Campo de busca não encontrado.")

        campo.clear()
        campo.send_keys(self.TERMO)
        campo.send_keys(Keys.RETURN)

        # Aguarda a URL mudar para página de resultados
        try:
            WebDriverWait(self.driver, TIMEOUT).until(
                lambda d: self.TERMO in d.current_url.lower()
                          or "busca" in d.current_url.lower()
                          or "search" in d.current_url.lower()
            )
        except TimeoutException:
            self._screenshot("busca_timeout")
            self.fail("URL de resultados não carregou no tempo esperado.")

        print(f"  ✅ Busca por '{self.TERMO}' redirecionou para: {self.driver.current_url}")

    def test_03_resultado_contem_cards_de_produto(self):
        """Página de resultados deve conter ao menos 1 card de produto."""
        # Reutiliza o estado da busca anterior navegando diretamente
        self._go(f"/busca/{self.TERMO}")
        card_selectors = [
            (By.CSS_SELECTOR, "[class*='product-card' i]"),
            (By.CSS_SELECTOR, "[class*='ProductCard' i]"),
            (By.CSS_SELECTOR, "[data-testid*='product' i]"),
            (By.CSS_SELECTOR, "li[class*='item' i]"),
        ]
        cards = []
        for by, value in card_selectors:
            cards = self.driver.find_elements(by, value)
            if cards:
                break

        self.assertGreater(len(cards), 0, "Nenhum card de produto encontrado nos resultados.")
        print(f"  ✅ {len(cards)} card(s) de produto encontrado(s).")


# ──────────────────────────────────────────────
# TC-03 · Navegação por categorias
# ──────────────────────────────────────────────
class TC03_Categorias(AmericanasBaseTest):

    def test_01_menu_de_departamentos_presente(self):
        """Menu / navbar de departamentos deve estar na homepage."""
        self._go()
        selectors = [
            (By.CSS_SELECTOR, "nav"),
            (By.CSS_SELECTOR, "[class*='menu' i]"),
            (By.CSS_SELECTOR, "[class*='department' i]"),
            (By.CSS_SELECTOR, "[class*='categoria' i]"),
        ]
        found = False
        for by, value in selectors:
            try:
                self.driver.find_element(by, value)
                found = True
                break
            except NoSuchElementException:
                continue
        self.assertTrue(found, "Menu/Navbar não encontrado.")
        print("  ✅ Menu de navegação presente.")

    def test_02_acesso_via_url_de_categoria(self):
        """Acessar URL de categoria de celulares deve carregar a página."""
        self._go("/celulares-e-smartphones")
        time.sleep(3)   # aguarda renderização inicial (SPA)
        url = self.driver.current_url
        # Não deve redirecionar para 404 ou página de erro
        self.assertNotIn("404", self.driver.title.lower())
        self.assertNotIn("erro", self.driver.title.lower())
        print(f"  ✅ Categoria carregada: {url}")


# ──────────────────────────────────────────────
# TC-04 · Página de produto
# ──────────────────────────────────────────────
class TC04_PaginaDeProduto(AmericanasBaseTest):

    def _get_first_product_url(self):
        """Navega para busca e retorna URL do primeiro produto."""
        self._go("/busca/smartphone")
        time.sleep(3)
        links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/produto/']")
        if not links:
            links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='-id-']")
        return links[0].get_attribute("href") if links else None

    def test_01_pagina_de_produto_carrega(self):
        """Deve conseguir acessar a página de detalhe de um produto."""
        url = self._get_first_product_url()
        if not url:
            self.skipTest("Nenhum link de produto encontrado nos resultados.")
        self.driver.get(url)
        time.sleep(3)
        self.assertNotIn("404", self.driver.title.lower())
        print(f"  ✅ Produto acessado: {self.driver.title[:60]}")

    def test_02_nome_do_produto_visivel(self):
        """Título/nome do produto deve estar presente na página."""
        url = self._get_first_product_url()
        if not url:
            self.skipTest("Nenhum link de produto encontrado nos resultados.")
        self.driver.get(url)
        time.sleep(3)
        selectors = [
            (By.CSS_SELECTOR, "h1"),
            (By.CSS_SELECTOR, "[class*='product-name' i]"),
            (By.CSS_SELECTOR, "[class*='ProductName' i]"),
            (By.CSS_SELECTOR, "[data-testid*='name' i]"),
        ]
        titulo = None
        for by, value in selectors:
            try:
                titulo = self.driver.find_element(by, value)
                break
            except NoSuchElementException:
                continue
        self.assertIsNotNone(titulo, "Nome do produto não encontrado.")
        print(f"  ✅ Nome do produto: {titulo.text[:60]}")

    def test_03_preco_visivel(self):
        """Preço do produto deve estar presente na página."""
        url = self._get_first_product_url()
        if not url:
            self.skipTest("Nenhum link de produto encontrado nos resultados.")
        self.driver.get(url)
        time.sleep(3)
        selectors = [
            (By.CSS_SELECTOR, "[class*='price' i]"),
            (By.CSS_SELECTOR, "[class*='Price' i]"),
            (By.CSS_SELECTOR, "[data-testid*='price' i]"),
        ]
        preco = None
        for by, value in selectors:
            els = self.driver.find_elements(by, value)
            for el in els:
                if "R$" in el.text or el.text.strip():
                    preco = el
                    break
            if preco:
                break
        self.assertIsNotNone(preco, "Preço não encontrado na página do produto.")
        print(f"  ✅ Preço encontrado: {preco.text[:30]}")


# ──────────────────────────────────────────────
# TC-05 · Performance básica
# ──────────────────────────────────────────────
class TC05_Performance(AmericanasBaseTest):

    def test_01_homepage_carrega_em_menos_de_15s(self):
        """Homepage deve carregar em menos de 15 segundos."""
        inicio = time.time()
        self._go()
        # Aguarda ao menos o body estar presente
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        elapsed = time.time() - inicio
        self.assertLess(elapsed, 15, f"Homepage demorou {elapsed:.1f}s (limite: 15s)")
        print(f"  ✅ Homepage carregada em {elapsed:.2f}s")

    def test_02_busca_carrega_em_menos_de_15s(self):
        """Resultados de busca devem aparecer em menos de 15 segundos."""
        inicio = time.time()
        self._go("/busca/televisao")
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        elapsed = time.time() - inicio
        self.assertLess(elapsed, 15, f"Busca demorou {elapsed:.1f}s (limite: 15s)")
        print(f"  ✅ Página de busca carregada em {elapsed:.2f}s")


# ──────────────────────────────────────────────
# Ponto de entrada
# ──────────────────────────────────────────────
if __name__ == "__main__":
    loader  = unittest.TestLoader()
    suite   = unittest.TestSuite()

    # Ordem dos test cases
    for tc in [TC01_Homepage, TC02_Busca, TC03_Categorias,
               TC04_PaginaDeProduto, TC05_Performance]:
        suite.addTests(loader.loadTestsFromTestCase(tc))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
