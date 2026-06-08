from odoo import models, fields


class MedicalAttestationTemplate(models.Model):
    _name = 'medical.attestation.template'
    _description = 'Modèle d\'attestation médicale'
    _order = 'sequence, name'

    name = fields.Char(string='Nom du modèle', required=True)
    title = fields.Char(string='Titre du document', required=True,
                        help="Titre qui apparaîtra sur l'attestation imprimée. Ex: Certificat médical d'aptitude")
    content = fields.Text(string='Contenu par défaut',
                          help="Texte pré-rempli lors de la sélection de ce modèle. "
                               "Le médecin pourra le modifier pour chaque attestation.")
    active = fields.Boolean(string='Actif', default=True)
    sequence = fields.Integer(string='Séquence', default=10)
