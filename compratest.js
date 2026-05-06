const {By, until} = require ('selenium-webdriver');
const {criarDriver} = require ('./helpers/driver');
const {expect} = require ('chai');

describe ('Teste de Compra (Checkout)' , function(){
    let driver;
    before (async () => {
        driver = await criarDriver();

    });

    after (async() => {
        await driver.quit();
    });

    it('deve completar o fluxo de compra' , async() => {
        await driver.get('https://localhost:3000/produtos');
        await driver.findElement(By.css('.produto-card:first-child .btn-adicional')).click();

        await driver.get ('http://localhost:3000/carrinho');
        await driver.findElement(By.css('btn-finalizar')).click();

        await driver.wait(until.urlContains('/checkout'), 5000);
        await driver.findElement(By.id('nome')).sendKeys('Lucas Teste');
        await driver.findElement(By.id('endereco')).sendKeys('Rua um');
        await driver.findElement(By.id('cep')).sendKeys('1000-1000');

        await driver.findElement(By.css('.btn-confirmar-pedido')).click();

        const confirmacao = await driver.wait(
            until.elementsLocated(By.css('.mensagem-sucesso')), 8000

        );
        const texto = await confirmacao.getText();
        expect(texto).to.include('Pedido realizado');
    });
});
