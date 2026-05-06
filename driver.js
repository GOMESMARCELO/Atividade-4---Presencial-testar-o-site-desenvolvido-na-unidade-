const {Builder} = require ('selenium-webdriver');
const chrome = require ('selenium-webdriver/chrome');

async function criarDriver(){
    const options = new chrome.Options();

    const driver = await new Builder()
    .forBrowser('chrome')
    .setChromeOptions(options)
    .build();

    return driver;
}

module.exports = {criarDriver};