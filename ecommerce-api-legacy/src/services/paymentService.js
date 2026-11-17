const config = require('../config');

class PaymentService {
    static maskCard(cardNumber) {
        if (!cardNumber || cardNumber.length < 4) return "****";
        const last4 = cardNumber.slice(-4);
        return `****-****-****-${last4}`;
    }

    static processPayment(cardNumber, amount) {
        const masked = PaymentService.maskCard(cardNumber);
        // Regra de negócio: cartões iniciados em 4 são aprovados
        const status = (typeof cardNumber === 'string' && cardNumber.startsWith("4")) ? "PAID" : "DENIED";
        return {
            status,
            amount,
            maskedCard: masked
        };
    }
}

module.exports = PaymentService;
