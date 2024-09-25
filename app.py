from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time

# variaveis
driver_path = ''        # Caminho para o driver do navegador
login = ''              # Login da plataforma MeuRH
password = ''           # Senha da plataforma MeuRH
start_time = '08:00'    # Horário de entrada
end_time = '17:48'      # Horário de saída
justification = '.'     # Justificativa da batida em atraso

# Inicializar o Service do Edge com o caminho do msedgedriver
service = Service(executable_path=driver_path)

# Inicializar o WebDriver do Navegador
driver = webdriver.Edge(service=service)

# deixa tela cheia
driver.maximize_window()

# Acessar a página de login
driver.get('https://actconsultoria146752.protheus.cloudtotvs.com.br:1804/meurh01/#/login')

time.sleep(1)

# Localizar o campo de input pelo atributo placeholder e digitar o usuário
xpath = "//input[@placeholder='Informe o seu usuário']"
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
user_field = driver.find_element(By.XPATH, xpath)
user_field.send_keys(login)

# Localizar o campo de input pelo atributo placeholder e digitar a senha
xpath = "//input[@placeholder='Informe sua senha']"
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
password_field = driver.find_element(By.XPATH, xpath)
password_field.send_keys(password)

# Clica pra logar
xpath = "//*[text()='Entrar']"
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
login_button = driver.find_element(By.XPATH, xpath)
login_button.click()

# Aguarda processar o login
time.sleep(3)

# Acessar a página de espelho de ponto
driver.get('https://actconsultoria146752.protheus.cloudtotvs.com.br:1804/meurh01/#/timesheet/clockings')

# Aguarda ter redenrizado pelo menos a primeira row na tabela de ponto
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="table-timesheet"]/tbody/tr[1]')))

# Encontra o elemento <tbody> dentro do elemento <table> com id = 'table-timesheet' 
tbody = driver.find_element(By.ID, "table-timesheet").find_element(By.TAG_NAME, "tbody")

# Veirifca a quantidade de elementos <tr> dentro do <tbody>
rows = tbody.find_elements(By.TAG_NAME, "tr")
rows_count = len(rows)

# Inverte a ordem
# rows = rows[::-1]

# Itera sobre cada 'tr'
#for row in rows:
for i in range(rows_count):
    # Coleta todos os elementos 'td' da row atual
    #tds = row.find_elements(By.TAG_NAME, "td")
    
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="table-timesheet"]/tbody/tr[1]'))) # Aguarda ter redenrizado pelo menos a primeira row na tabela de ponto
    tbody = driver.find_element(By.ID, "table-timesheet").find_element(By.TAG_NAME, "tbody") # Encontra o elemento <tbody> dentro do elemento <table> com id = 'table-timesheet' 
    rows = tbody.find_elements(By.TAG_NAME, "tr") # Coleta todos os elementos <tr> dentro do <tbody>
    tds = rows[i].find_elements(By.TAG_NAME, "td") # Coleta todos os elementos td dentro do tr
    
    if len(tds) >= 4:
        date_cell = tds[0] 
        entry_cell = tds[1]
        exit_cell = tds[2]
        button_cell = tds[3]
 
        # encontra a tag 'a' e os elementos 'span' do date_cell
        spans = date_cell.find_elements(By.TAG_NAME, "span")
        date = '' 
        week = ''
        if len(spans) > 0:
            date = spans[0].text
            # Para o dia, pegar os dois primeiros caracteres e convertê-los em um número
            day = int(date[:2])
        if len(spans) > 1:
            week = spans[1].text

        # Obtem o dia atual
        current_day = datetime.now().day

        # Ignoramos dias do futuro
        if(day <= current_day):
            # Ignoramos sábado e domingo
            if(week != '' and week != 'sábado' and week != 'domingo'):  
                # Ignoramos se ja exitir qualquer marcação no dia
                if (not entry_cell.find_elements(By.XPATH, "./*")) and (not exit_cell.find_elements(By.XPATH, "./*")):
                    print('Marcando ponto do dia ' + date + ', ' + week)
                    
                    # Clica para abrir o dropdown de opcoes
                    open_dropbown_button = button_cell.find_element(By.TAG_NAME, "span")
                    open_dropbown_button.click()
                    
                    # Clica na segunda opção do dropdown para incluir marcação
                    WebDriverWait(button_cell, 10).until(EC.element_to_be_clickable((By.TAG_NAME, "li")))
                    include_time_option = button_cell.find_elements(By.TAG_NAME, "li")[1]
                    include_time_option.click()
                    time.sleep(1)

                    # Prossegue para incluir duas marcações, uma de entrada e outra de saída
                    for k in range(2):
                        # Separar a string em horas e minutos
                        hour = '00'
                        minutes = '00'
                        if(k == 0): # entrada
                            hour, minutes = start_time.split(':') # se mandar de uma vez, o front-end diz que a formatação está incorreta... mas separando em dois funciona
                        else: # saída
                            hour, minutes = end_time.split(':')
                        
                        # Localiza o campo de input pelo atributo placeholder, e insere o horário de entrada ou saída
                        xpath = "//input[@placeholder='Insira o horário no formato 00:00']"
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
                        time_field = driver.find_element(By.XPATH, xpath)
                        time_field.send_keys(hour) 
                        time_field.send_keys(minutes)

                        time.sleep(1)

                        # Clica no campo radial de entrada ou saída
                        if(k==0): # entrada
                            xpath = '//*[@id="rdb-direction-clocking"]/po-field-container/div/div[3]/div[1]'
                        else: # saída
                            xpath = '//*[@id="rdb-direction-clocking"]/po-field-container/div/div[3]/div[2]'
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
                        radial_field = driver.find_element(By.XPATH, xpath)
                        radial_field.click()

                        time.sleep(1)

                        # Clica para abrir o dropdown do motivo
                        xpath = '//*[@id="sel-reason"]/po-field-container/div/div[2]'
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
                        dropdown_field = driver.find_element(By.XPATH, xpath)
                        dropdown_field.click()

                        time.sleep(1)

                        # Clica na primeira opção do dropdown para incluir o motivo
                        WebDriverWait(dropdown_field, 10).until(EC.element_to_be_clickable((By.TAG_NAME, "li")))
                        reason_option = dropdown_field.find_elements(By.TAG_NAME, "li")[0]
                        reason_option.click()

                        time.sleep(1)

                        # Localizar o campo de input pelo atributo placeholder e digita a justificativa
                        xpath = "//textarea[@placeholder='Escreva a sua justificativa']"
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
                        justify_field = driver.find_element(By.XPATH, xpath)
                        justify_field.send_keys(justification)

                        time.sleep(1)

                        # Clica pra confimar a marcação
                        xpath = "//*[text()='Confirmar']"
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
                        confirm_button = driver.find_element(By.XPATH, xpath)
                        confirm_button.click()

                        time.sleep(1)

                        # Aguarda marcação dar sucesso
                        # xpath = "//*[text()='Batida inserida com sucesso']"
                        # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))

                        if(k==0):
                            # Falta bater a saída, clica para incluir nova batida
                            xpath = "//*[text()='Incluir nova batida']"
                            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
                            new_entry_button = driver.find_element(By.XPATH, xpath)
                            new_entry_button.click()
                            time.sleep(1)
                    
                    time.sleep(3)
                    # Volta para a página anterior
                    driver.back()
                    time.sleep(1)

print('Finalizado')
time.sleep(2)

# Fechar o navegador
driver.quit()
