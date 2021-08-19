from unittest import TestCase

class TestPrep(TestCase):
    """Test prep.py."""

    def test_chs_remap_onlyEEG(self):
        import chs_remap_onlyEEG
        #  define srg_synergy_epochs
        cons = SPMI_1epoch(srg_synergy_epochs.get_data()[0], 3, 1)
        ch_name_order_cons = srg_synergy_epochs.info['ch_names']
        pareticSide = 'l'
        chs_list_preImage = None
        chs_list_image = None
        cons_remapped = chs_remap_onlyEEG(cons, ch_name_order_cons, pareticSide)
        # print(chs_list_preImage)
        # print(chs_list_image)
        # print(ch_name_order_cons)
        # the first element of cons_remapped is FP1 and AF3, it is 16 and 30 in ch_name_order_cons
        assert cons[16,30]) == cons_remapped[0,1], "unsuccessful remapping"