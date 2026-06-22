from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import logging
import pytz

_logger = logging.getLogger(__name__)


class TestCasLimites(TransactionCase):


    def setUp(self):
        super().setUp()

        self.specialite = self.env['medical.specialty'].create({
            'name': 'Médecine générale Test',
        })


        self.medecin1 = self.env['medical.doctor'].create({
            'first_name': 'Test',
            'last_name': 'Un',
            'specialty_id': self.specialite.id,
        })
        self.medecin2 = self.env['medical.doctor'].create({
            'first_name': 'Test',
            'last_name': 'Deux',
            'specialty_id': self.specialite.id,
        })

        # Patients
        self.patient1 = self.env['medical.patient'].create({
            'first_name': 'Alice',
            'last_name': 'Dupont',
            'email': 'alice@test.fr',
            'phone': '0600000001',
            'birth_date': '1990-01-01',
            'gender': 'female',
        })
        self.patient2 = self.env['medical.patient'].create({
            'first_name': 'Bob',
            'last_name': 'Martin',
            'email': 'bob@test.fr',
            'phone': '0600000002',
            'birth_date': '1985-06-15',
            'gender': 'male',
        })



        self.creneau_utc = self._creneau_valide(self.medecin1)

    def _creneau_valide(self, medecin, jour_cible=0, decalage_semaines=1):
        paris = pytz.timezone('Europe/Paris')

        # Disponibilité du jour cible (0 = lundi)
        dispo = medecin.availability_ids.filtered(
            lambda a: a.day_of_week == str(jour_cible)
        )
        self.assertTrue(
            dispo and dispo.slot_ids,
            "Le médecin doit avoir au moins un créneau configuré le jour cible.",
        )
        # Premier créneau disponible (start_hour en float, ex: 10.0 = 10h00)
        slot = dispo.slot_ids.sorted(lambda s: s.start_hour)[0]
        heures = int(slot.start_hour)
        minutes = int(round((slot.start_hour - heures) * 60))

        # Trouver le prochain lundi à venir
        aujourdhui = datetime.now(paris)
        jours_avant = (jour_cible - aujourdhui.weekday()) % 7
        if jours_avant == 0:
            jours_avant = 7  # toujours dans le futur
        cible = aujourdhui + timedelta(days=jours_avant + 7 * (decalage_semaines - 1))

        local_dt = paris.localize(datetime(
            cible.year, cible.month, cible.day, heures, minutes, 0
        ))
        return local_dt.astimezone(pytz.utc).replace(tzinfo=None)

    # cas 1 : Double réservation du même créneau

    def test_01_double_reservation_meme_creneau(self):
        rdv1 = self.env['medical.appointment'].create({
            'patient_id': self.patient1.id,
            'doctor_id': self.medecin1.id,
            'appointment_date': self.creneau_utc,
            'state': 'draft',
        })
        self.assertTrue(rdv1.id, "Le premier rendez-vous doit être créé sans erreur.")

        with self.assertRaises(ValidationError,
                msg="Le système doit refuser un double créneau."):
            self.env['medical.appointment'].create({
                'patient_id': self.patient2.id,
                'doctor_id': self.medecin1.id,
                'appointment_date': self.creneau_utc,
                'state': 'draft',
            })

        _logger.info("TEST CAS 1 (double réservation même créneau) a réussi.")

    # cas 3 : Médecin absent, annulation des RDV concernés              #

    def test_03_medecin_absent_annule_rdvs(self):
        rdv = self.env['medical.appointment'].create({
            'patient_id': self.patient1.id,
            'doctor_id': self.medecin1.id,
            'appointment_date': self.creneau_utc,
            'state': 'confirmed',
        })
        self.assertEqual(rdv.state, 'confirmed')

        rdv.action_cancel()

        self.assertEqual(
            rdv.state, 'cancelled',
            "Le RDV doit passer en 'annulé' quand le médecin est marqué absent.",
        )

        _logger.info("TEST CAS 3 (médecin absent, RDV annulé) a réussi.")