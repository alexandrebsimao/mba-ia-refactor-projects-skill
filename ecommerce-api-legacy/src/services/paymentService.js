const APPROVED_CARD_PREFIX = "4";

class PaymentService {
    static maskCard(cardNumber) {
        if (!cardNumber || cardNumber.length < 4) return "****";
        const last4 = cardNumber.slice(-4);
        return `****-****-****-${last4}`;
    }

    static processPayment(cardNumber, amount) {
        const masked = PaymentService.maskCard(cardNumber);
        const status = (typeof cardNumber === 'string' && cardNumber.startsWith(APPROVED_CARD_PREFIX))
            ? "PAID"
            : "DENIED";
        return {
            status,
            amount,
            maskedCard: masked
        };
    }
}

module.exports = PaymentService;
