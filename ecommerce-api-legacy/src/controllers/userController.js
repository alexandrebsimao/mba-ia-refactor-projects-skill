const UserModel = require('../models/userModel');

class UserController {
    static async deleteUser(req, res, next) {
        try {
            const { id } = req.params;
            await UserModel.deleteWithCascade(id);
            return res.status(200).json({ msg: "Usuário e registros associados deletados com sucesso." });
        } catch (err) {
            next(err);
        }
    }
}

module.exports = UserController;
