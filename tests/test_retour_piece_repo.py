# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch, MagicMock
from models.retour_piece import RetourPiece
from repositories import retour_piece_repo

class TestRetourPieceRepo(unittest.TestCase):
    @patch('repositories.retour_piece_repo.get_db')
    def test_create_retour(self, mock_get_db):
        # Setup mock DB connection and cursor
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_get_db.return_value.__enter__.return_value = (mock_cur, mock_conn)
        
        # Setup mock fetchone return value
        mock_cur.fetchone.return_value = (1, '2026-07-23')
        
        ret = RetourPiece(piece_id=10, quantite=2, motif='Defect', fournisseur_id=5)
        created_ret = retour_piece_repo.create_retour(ret)
        
        # Verify query execution
        mock_cur.execute.assert_called_once()
        self.assertEqual(created_ret.id, 1)
        self.assertEqual(created_ret.date_retour, '2026-07-23')

    @patch('repositories.retour_piece_repo.get_db')
    def test_get_by_id(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_get_db.return_value.__enter__.return_value = (mock_cur, mock_conn)
        
        # Simulate DB returning a row
        mock_cur.fetchone.return_value = (1, 10, 2, 'Defect', '2026-07-23', 5)
        
        ret = retour_piece_repo.get_by_id(1)
        
        mock_cur.execute.assert_called_once()
        self.assertIsNotNone(ret)
        self.assertEqual(ret.id, 1)
        self.assertEqual(ret.piece_id, 10)
        self.assertEqual(ret.motif, 'Defect')

    @patch('repositories.retour_piece_repo.get_db')
    def test_get_all(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_get_db.return_value.__enter__.return_value = (mock_cur, mock_conn)
        
        mock_cur.fetchall.return_value = [
            (1, 10, 2, 'Defect', '2026-07-23', 5),
            (2, 12, 1, 'Wrong part', '2026-07-24', None)
        ]
        
        results = retour_piece_repo.get_all()
        
        mock_cur.execute.assert_called_once()
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].id, 1)
        self.assertEqual(results[1].motif, 'Wrong part')

if __name__ == '__main__':
    unittest.main()
