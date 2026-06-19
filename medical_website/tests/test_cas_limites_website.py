from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import pytz


class TestCasLimitesWebsite(TransactionCase):
    """
    Cas limites côté website — medical_website
    Réf. cahier des charges §13 : annulation interdite à moins de 2h.

    Prérequis : la méthode action_cancel_website() doit exister sur
    medical.appointment (voir snippet_action_cancel_website.py).
    """

    def setUp(self):
        super().setUp()

        self.specialite = self.env['medical.specialty'].create({
            'name': 'Médecine générale Test Website',
        })

        # Médecin sans user_id (dispos Lun-Ven auto-créées par medical_base)
        self.medecin = self.env['medical.doctor'].create({
            'first_name': 'Web',
            'last_name': 'Test',
            'specialty_id': self.specialite.id,
        })

        self.patient = self.env['medical.patient'].create({
            'first_name': 'Claire',
            'last_name': 'Bernard',
            'email': 'claire@test.fr',
            'phone': '0600000003',
            'birth_date': '1992-03-20',
            'gender': 'female',
        })

    def _creneau_valide(self, jour_cible=0, decalage_semaines=1):
        """Prochain jour cible, sur le 1er créneau réel du médecin (heure Paris)."""
        paris = pytz.timezone('Europe/Paris')
        dispo = self.medecin.availability_ids.filtered(
            lambda a: a.day_of_week == str(jour_cible)
        )
        slot = dispo.slot_ids.sorted(lambda s: s.start_hour)[0]
        heures = int(slot.start_hour)
        minutes = int(round((slot.start_hour - heures) * 60))

        aujourdhui = datetime.now(paris)
        jours_avant = (jour_cible - aujourdhui.weekday()) % 7
        if jours_avant == 0:
            jours_avant = 7
        cible = aujourdhui + timedelta(days=jours_avant + 7 * (decalage_semaines - 1))
        local_dt = paris.localize(datetime(
            cible.year, cible.month, cible.day, heures, minutes, 0
        ))
        return local_dt.astimezone(pytz.utc).replace(tzinfo=None)

    def _creer_rdv_puis_forcer_date(self, date_cible_utc):
        """
        Crée un RDV sur un créneau valide (pour passer la contrainte de
        disponibilité), puis force sa date à la valeur voulue en SQL afin
        de tester l'annulation sans rejouer les contraintes de création.
        """
        rdv = self.env['medical.appointment'].create({
            'patient_id': self.patient.id,
            'doctor_id': self.medecin.id,
            'appointment_date': self._creneau_valide(),
            'state': 'confirmed',
        })
        # Écriture directe en base pour contourner les @api.constrains
        self.env.cr.execute(
            "UPDATE medical_appointment SET appointment_date = %s WHERE id = %s",
            (date_cible_utc, rdv.id),
        )
        rdv.invalidate_recordset(['appointment_date'])
        return rdv

    # ------------------------------------------------------------------ #
    # CAS 2 : Annulation moins de 2h avant le RDV — doit être bloquée    #
    # ------------------------------------------------------------------ #
    def test_02_annulation_moins_2h_bloquee(self):
        dans_1h = datetime.utcnow() + timedelta(hours=1)
        rdv = self._creer_rdv_puis_forcer_date(dans_1h.replace(microsecond=0))

        with self.assertRaises(ValidationError, msg=(
            "L'annulation moins de 2h avant le RDV doit être bloquée "
            "avec un message demandant d'appeler le secrétariat."
        )):
            rdv.action_cancel_website()

    # ------------------------------------------------------------------ #
    # CAS 2b : Annulation plus de 2h avant — doit passer                 #
    # ------------------------------------------------------------------ #
    def test_02b_annulation_plus_2h_autorisee(self):
        dans_5h = datetime.utcnow() + timedelta(hours=5)
        rdv = self._creer_rdv_puis_forcer_date(dans_5h.replace(microsecond=0))

        try:
            rdv.action_cancel_website()
        except ValidationError as e:
            self.fail(f"Un RDV dans plus de 2h ne devrait pas être bloqué : {e}")

        self.assertEqual(
            rdv.state, 'cancelled',
            "Le RDV doit passer en 'cancelled' quand l'annulation est faite à temps.",
        )