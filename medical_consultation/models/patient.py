from odoo import models, fields, api

class MedicalPatient(models.Model):
    _inherit = 'medical.patient'

    consultation_ids = fields.One2many('medical.consultation', 'patient_id', string='Consultations')
    consultation_count = fields.Integer(
        string='Nombre de consultations',
        compute='_compute_consultation_count',
        store=False,
    )

    @api.depends('consultation_ids')
    def _compute_consultation_count(self):
        for patient in self:
            patient.consultation_count = len(patient.consultation_ids)

    def action_view_consultations(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Consultations',
            'res_model': 'medical.consultation',
            'view_mode': 'list,form',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
        }
