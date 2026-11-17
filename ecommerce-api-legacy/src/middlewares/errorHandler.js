function errorHandler(err, req, res, next) {
    console.error(`[ERROR] ${req.method} ${req.url} - ${err.message}`);
    return res.status(err.status || 500).json({
        erro: err.message || "Erro interno do servidor",
        sucesso: false
    });
}

module.exports = errorHandler;
