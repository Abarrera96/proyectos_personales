from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
import json
import time

class Reviews:
    def __init__(self, asin) -> None:
        """
        Constructor de la clase Reviews.
        Inicializa el navegador y configura la URL base para las reseñas del producto especificado por el ASIN.
        
        :param asin: ASIN (Amazon Standard Identification Number) del producto.
        """
        self.asin = asin
        # Inicializa el navegador Chrome usando WebDriver Manager, que se encarga de descargar automáticamente
        # el driver correcto para la versión actual de Chrome instalada en el sistema.
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        # URL base para acceder a las reseñas del producto. Se incluirá el número de página en las solicitudes.
        self.url = f'https://www.amazon.es/Apple-iPhone-128GB-Azul-Reacondicionado/product-reviews/{self.asin}/ref=cm_cr_arp_d_viewopt_srt?ie=UTF8&reviewerType=all_reviews&sortBy=recent&pageNumber='

    def pagination(self, page):
        """
        Navega a una página específica de reseñas y recupera los elementos de reseña.
        
        :param page: Número de página a recuperar.
        :return: Lista de elementos de reseñas si están presentes, de lo contrario False.
        """
        self.driver.get(self.url + str(page))
        time.sleep(5)  # Espera 5 segundos para asegurar que la página se haya cargado completamente.
        # Busca todos los elementos que contienen reseñas basándose en su atributo data-hook.
        reviews = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-hook="review"]')
        return reviews if reviews else False

    def parse(self, reviews):
        """
        Extrae y parsea la información relevante de cada elemento de reseña.
        
        :param reviews: Lista de elementos de reseñas a parsear.
        :return: Lista de diccionarios con la información parseada de las reseñas.
        """
        total = []
        for review in reviews:
            try:
                # Extrae el título, el rating y el cuerpo de cada reseña.
                title = review.find_element(By.CSS_SELECTOR, 'a[data-hook="review-title"]').text
                rating_element = review.find_element(By.CSS_SELECTOR, 'i[data-hook="review-star-rating"]')
                rating = rating_element.find_element(By.CSS_SELECTOR, '.a-icon-alt').get_attribute('textContent')
                body = review.find_element(By.CSS_SELECTOR, 'span[data-hook="review-body"]').text.replace('\n', '').strip()
                
                # Compila la información extraída en un diccionario y lo añade a la lista total.
                data = {
                    'title': title,
                    'rating': rating, 
                    'body': body[:1000]  # Limita el cuerpo a 1000 caracteres para evitar textos excesivamente largos.
                }
                total.append(data)
            except NoSuchElementException:
                print("Element not found, skipping...")
        return total
    
    def save(self, results):
        """
        Guarda las reseñas extraídas en un archivo JSON.
        
        :param results: Lista de diccionarios con la información de las reseñas.
        """
        with open(f'selenium_amazon_product_asin_{self.asin}_reviews.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
    
    def close(self):
        """
        Cierra el navegador al finalizar el proceso.
        """
        self.driver.quit()

if __name__ == '__main__':
    # Instancia la clase Reviews con el ASIN del producto deseado.
    # IMPORTANTE: seguramente te pueda salir nada más ejecutar este script un CAPTCHA, tienes que rellenarlo manualmente y ya se ejecutará todo bien 
    #             (tienes 3-5 segundos asi que se rápido! <3)
    amz_reviews = Reviews(asin='B08PCCJP5C')
    results = []
    # Itera sobre las páginas de reseñas hasta que no haya más o se alcance el límite establecido.
    for x in range(1, 100):
        print(f'Getting page {x}')
        reviews_elements = amz_reviews.pagination(x)
        if reviews_elements:
            # Parsea las reseñas de la página actual y las añade a los resultados.
            page_results = amz_reviews.parse(reviews_elements)
            results.extend(page_results)
        else:
            print('No more pages')
            break
    # Guarda los resultados en un archivo JSON y cierra el navegador.
    amz_reviews.save(results)
    amz_reviews.close()