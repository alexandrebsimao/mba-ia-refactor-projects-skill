const express = require('express');
const config = require('./config');
const db = require('./database/connection');
const apiRoutes = require('./routes');
const errorHandler = require('./middlewares/errorHandler');

const app = express();
app.use(express.json());

// Registra rotas da API sob /api
app.use('/api', apiRoutes);

// Middleware centralizado de tratamento de erros
app.use(errorHandler);

// Inicializa o banco de dados e expõe a aplicação
const initPromise = db.initDb();

if (require.main === module) {
    initPromise.then(() => {
        app.listen(config.port, () => {
            console.log(`LMS API refatorada rodando na porta ${config.port}...`);
        });
    }).catch(err => {
        console.error("Erro fatal ao inicializar banco de dados:", err);
        process.exit(1);
    });
}

module.exports = { app, initPromise };
