const {By, until} = require ('selenium-webdriver');
const {criarDriver} = require('./helpers/driver');
const { expect } = require('chai');

describe ('Teste de carrinho' , function () {
    let driver;
    before (async () => {
        driver = await criarDriver();
    });

    after(async () => {
    await driver.quit();
  });

  it ('deve adicionar produto ao carrinho' , async () => {
    await driver.get ('http://localhost:3000/produtos');
    await driver.findElement(By.css('produto-card:first-child .btn-adicionar')).click();
    await driver.wait(until.urlContains('/carrinho'), 5000);
    
    const itens = await driver.findElements(By.css('.item-carrinho'));
    expect(itens.lenght).to.be.greaterThan(0);

});

it ('deve remover porudot do carrinho' , async() => {
    await driver.get('http://localhost:3000/carrinho');
    const btnRemover = await driver.findElement(By.css('.btn-remover'));
    await btnRemover.click();

    await driver.sleep(1000);
    const itens = await driver.findElements(By.css('.item-carrinho'));
    expect(itens.lenght).to.equal(0);
});



});