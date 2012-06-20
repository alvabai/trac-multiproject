from multiproject.core.test.cqdetestcase import CQDETestCase
from multiproject.core.ssh_keys import SshKey, CQDESshKeyStore
from ..ConfigurationStub import conf
import tempfile
import os
import shutil

class SshKeysTestCase(CQDETestCase):

    def setUp(self):
        """empty"""

    def tearDown(self):
        """empty"""

    def test_create_from_row(self):
        # key_id, user_id, ssh_key, comment, added
        row =["37",  
        "2903",  
        "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAsEctmRR8YdO+nnZauPqhhsvOn6c30szVe1Gqmc6kM8/Wi9XS+dUKAL12iuQTrkuFCY6wvmfLG9ACIV8b1ZXxOxE3G5Q+0FvGJMHCdKL0b2fDCLiDNpcg22xOb4QaXggJaXR+M8yxNn5I+LIKpSA6vP6HEYKxm3aHQyrYDhy7WuJ8L/BUw+cAxDa0+y9l9ZuKwv5IdNTwU/WdQWeBXiLyhEV6Pcnx6pTDjgJqtnTHePQ/Cm/pedIYoeamFZwWkabnoTPZPiKa+ATLNXXOBzvcV32f2EFW7957TodpL1Yhg/WPDcD/2ypGWgmtUmWhYxJhXAactaTiZni+nhVjEi9zmQ==",
        "Toimiva avain", 
        "2010-12-01 12:15:07"]
        new_key = SshKey.from_sql_row(row)
        self.assertTrue(new_key)
        self.assertEquals(new_key.key_id,"37")
        self.assertEquals(new_key.user_id,"2903")
        
 
    def test_create_from_row_error(self):
        row =["37",  
        "2903",  
        "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAsEctmRR8YdO+nnZauPqhhsvOn6c30szVe1Gqmc6kM8/Wi9XS+dUKAL12iuQTrkuFCY6wvmfLG9ACIV8b1ZXxOxE3G5Q+0FvGJMHCdKL0b2fDCLiDNpcg22xOb4QaXggJaXR+M8yxNn5I+LIKpSA6vP6HEYKxm3aHQyrYDhy7WuJ8L/BUw+cAxDa0+y9l9ZuKwv5IdNTwU/WdQWeBXiLyhEV6Pcnx6pTDjgJqtnTHePQ/Cm/pedIYoeamFZwWkabnoTPZPiKa+ATLNXXOBzvcV32f2EFW7957TodpL1Yhg/WPDcD/2ypGWgmtUmWhYxJhXAactaTiZni+nhVjEi9zmQ==",
        "2010-12-01 12:15:07"]
        new_key = SshKey.from_sql_row(row)
        self.assertEquals(new_key, None)
        
    def test_validate_key(self):
        key_string = "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAsEctmRR8YdO+nnZauPqhhsvOn6c30szVe1Gqmc6kM8/Wi9XS+dUKAL12iuQTrkuFCY6wvmfLG9ACIV8b1ZXxOxE3G5Q+0FvGJMHCdKL0b2fDCLiDNpcg22xOb4QaXggJaXR+M8yxNn5I+LIKpSA6vP6HEYKxm3aHQyrYDhy7WuJ8L/BUw+cAxDa0+y9l9ZuKwv5IdNTwU/WdQWeBXiLyhEV6Pcnx6pTDjgJqtnTHePQ/Cm/pedIYoeamFZwWkabnoTPZPiKa+ATLNXXOBzvcV32f2EFW7957TodpL1Yhg/WPDcD/2ypGWgmtUmWhYxJhXAactaTiZni+nhVjEi9zmQ=="
        result = SshKey.validate_key_string(key_string)
        
        self.assertTrue(result)

    def test_validate_key_error_none_key(self):
        key_string = None
        result = SshKey.validate_key_string(key_string)
        self.assertFalse(result)

    def test_validate_key_error_empty_key(self):
        key_string = ""
        result = SshKey.validate_key_string(key_string)
        self.assertFalse(result)

    def test_validate_key_error_garble(self):
        key_string = "aglktjdkfgh4ya485yaqbv27q5cta72xb4to927t4vbtc7qne7tk27atf4rdtk78t4o8a7to287dt2387t5823adth8a27t4538a273t5rad8fht7b4cx872ctv14acxv4vx724528375c2v83476238c5628736827356258376c286vuwertawcuyewtvaccuw63vtyecrftcauitcai8ca3cvbsvdhcajrtjhefjhewyvcejw@hrywcvhgwejawfcvtweerftcjawerfcajv3xc84bru6wjruyagtavc2iq2bx4%5tiq2c5tb4i5c78t587ctqixuhe45rgdsgdf,msdf-g.,ergtreaiy3w v834    92461x     t<yzb  32t"
        result = SshKey.validate_key_string(key_string)
        self.assertFalse(result)
        
    def test_validate_key_error_too_short_key(self):
        key_string = "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAsEctmRR8YdO+nnZauPqhhsvOn6c30szVe1Gqmc6"
        result = SshKey.validate_key_string(key_string)
        self.assertFalse(result)
                            
    def test_validate_key_error_too_long_key(self):
        key_string = "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAsEctmRR8YdO+nnZauPqhhsvOn6c30szVe1Gqmc6kM8/Wi9XS+dUKAL12iuQTrkuFCY6wvmfLG9ACIV8b1ZXxOxE3G5Q+0FvGJMHCdKL0b2fDCLiDNpcg22xOb4QaXggJaXR+M8yxNn5I+LIKpSA6vP6HEYKxm3aHQyrYDhy7WuJ8L/BUw+cAxDa0+y9l9ZuKwv5IdNTwU/WdQWeBXiLyhEV6Pcnx6pTDjgJqtnTHePQ/Cm/pedIYoeamFZwWkabnoTPZPiKa+ATLNXXOBzvcV32f2EFW7957TodpL1Yhg/WPDcD/2ypGWgmtUmWhYxJhXAactaTidfsgsertaefsdgasgsdgsasdcaxcexcaewcxffeaerwq3rqrseavreacaxra3245rxa23r2a5xq35q235x235x2x5q2Zni+nhVjEi9zmQ=="
        result = SshKey.validate_key_string(key_string)
        self.assertFalse(result)
            
    def test_validate_key_error_nonBase64_key(self):
        key_string = "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAsEctmRR8#YdO+nnZauPqhhsvOn6c30szVe1Gqmc6kM8/Wi9XS+dUKAL12iuQTrkuFCY6wvmfLG9ACIV8b1ZXxOxE3G5Q+0FvGJMHCdKL0b2fDCLiDNpcg22xOb4QaXggJaXR+M8yxNn5I+LIKpSA6vP6HEYKxm3aHQyrYDhy7WuJ8L/BUw+cAxDa0+y9l9ZuKwv5IdNTwU/WdQWeBXiLyhEV6Pcnx6pTDjgJqtnTHePQ/Cm/pedIYoeamFZwWkabnoTPZPiKa+ATLNXXOBzvcV32f2EFW7957TodpL1Yhg/WPDcD/2ypGWgmtUmWhYxJhXAactaTiZni+nhVjEi9zmQ=="
        result = SshKey.validate_key_string(key_string)
        self.assertFalse(result)
        
    def test_validate_key_error_invalid_key_header(self):
        key_string = "ssh-rsa ABAAB3NzaC1yc2EAAAABIwAAAQEAsEctmRR8YdO+nnZauPqhhsvOn6c30szVe1Gqmc6kM8/Wi9XS+dUKAL12iuQTrkuFCY6wvmfLG9ACIV8b1ZXxOxE3G5Q+0FvGJMHCdKL0b2fDCLiDNpcg22xOb4QaXggJaXR+M8yxNn5I+LIKpSA6vP6HEYKxm3aHQyrYDhy7WuJ8L/BUw+cAxDa0+y9l9ZuKwv5IdNTwU/WdQWeBXiLyhEV6Pcnx6pTDjgJqtnTHePQ/Cm/pedIYoeamFZwWkabnoTPZPiKa+ATLNXXOBzvcV32f2EFW7957TodpL1Yhg/WPDcD/2ypGWgmtUmWhYxJhXAactaTiZni+nhVjEi9zmQ=="
        result = SshKey.validate_key_string(key_string)
        self.assertFalse(result)

    def test_validate_key_error_invalid_key_type(self):
        key_string = "xsh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAsEctmRR8YdO+nnZauPqhhsvOn6c30szVe1Gqmc6kM8/Wi9XS+dUKAL12iuQTrkuFCY6wvmfLG9ACIV8b1ZXxOxE3G5Q+0FvGJMHCdKL0b2fDCLiDNpcg22xOb4QaXggJaXR+M8yxNn5I+LIKpSA6vP6HEYKxm3aHQyrYDhy7WuJ8L/BUw+cAxDa0+y9l9ZuKwv5IdNTwU/WdQWeBXiLyhEV6Pcnx6pTDjgJqtnTHePQ/Cm/pedIYoeamFZwWkabnoTPZPiKa+ATLNXXOBzvcV32f2EFW7957TodpL1Yhg/WPDcD/2ypGWgmtUmWhYxJhXAactaTiZni+nhVjEi9zmQ=="
        result = SshKey.validate_key_string(key_string)
        self.assertFalse(result)
                    
    def test_validate_key_error_invalid_key_padding(self):
        key_string = "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAsEctmRR8YdO+nnZauPqhhsvOn6c30szVe1Gqmc6kM8/Wi9XS+dUKAL12iuQTrkuFCY6wvmfLG9ACIV8b1ZXxOxE3G5Q+0FvGJMHCdKL0b2fDCLiDNpcg22xOb4QaXggJaXR+M8yxNn5I+LIKpSA6vP6HEYKxm3aHQyrYDhy7WuJ8L/BUw+cAxDa0+y9l9ZuKwv5IdNTwU/WdQWeBXiLyhEV6Pcnx6pTDjgJqtnTHePQ/Cm/pedIYoeamFZwWkabnoTPZPiKa+ATLNXXOBzvcV32f2EFW7957TodpL1Yhg/WPDcD/2ypGWgmtUmWhYxJhXAactaTiZni+nhVjEi9zmQ="
        result = SshKey.validate_key_string(key_string)
        self.assertFalse(result)

    def test_remove_comment_from_key(self):
        key_string = "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAsEctmRR8YdO+nnZauPqhhsvOn6c30szVe1Gqmc6kM8/Wi9XS+dUKAL12iuQTrkuFCY6wvmfLG9ACIV8b1ZXxOxE3G5Q+0FvGJMHCdKL0b2fDCLiDNpcg22xOb4QaXggJaXR+M8yxNn5I+LIKpSA6vP6HEYKxm3aHQyrYDhy7WuJ8L/BUw+cAxDa0+y9l9ZuKwv5IdNTwU/WdQWeBXiLyhEV6Pcnx6pTDjgJqtnTHePQ/Cm/pedIYoeamFZwWkabnoTPZPiKa+ATLNXXOBzvcV32f2EFW7957TodpL1Yhg/WPDcD/2ypGWgmtUmWhYxJhXAactaTiZni+nhVjEi9zmQ== ari.rusakko@digia.com on paras"
        result = SshKey.remove_comment_from_key_string(key_string)
        count = len(result.split())
        self.assertEquals(count, 2)
        key_string = "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAsEctmRR8YdO+nnZauPqhhsvOn6c30szVe1Gqmc6kM8/Wi9XS+dUKAL12iuQTrkuFCY6wvmfLG9ACIV8b1ZXxOxE3G5Q+0FvGJMHCdKL0b2fDCLiDNpcg22xOb4QaXggJaXR+M8yxNn5I+LIKpSA6vP6HEYKxm3aHQyrYDhy7WuJ8L/BUw+cAxDa0+y9l9ZuKwv5IdNTwU/WdQWeBXiLyhEV6Pcnx6pTDjgJqtnTHePQ/Cm/pedIYoeamFZwWkabnoTPZPiKa+ATLNXXOBzvcV32f2EFW7957TodpL1Yhg/WPDcD/2ypGWgmtUmWhYxJhXAactaTiZni+nhVjEi9zmQ=="
        result = SshKey.remove_comment_from_key_string(key_string)
        count = len(result.split())
        self.assertEquals(count, 2)        

    def test_remove_comment_from_key_error(self):
        key_string = None
        result = SshKey.remove_comment_from_key_string(key_string)
        self.assertEquals(result, None)

class CQDESshKeyStoreTestCase(CQDETestCase):

    def setUp(self):
        self.store = CQDESshKeyStore.instance()
        conf.use_test_db(True)
        self.tmp_root = tempfile.mkdtemp()
        self.load_fixtures()
        conf.memcached_enabled = False
        
    def tearDown(self):
        conf.use_test_db(False)
        shutil.rmtree(self.tmp_root)

    def test_get_ssh_key(self):
        user_id = 32
        list = self.store.get_ssh_keys_by_user_id(user_id)
        count = len(list)
        self.assertEquals(count, 1)
        text = list[0].description
        self.assertEquals(text, "Toimiva avain")
        
    def test_get_ssh_key_error(self):
        user_id = None
        list = self.store.get_ssh_keys_by_user_id(user_id)
        self.assertFalse(list)
        
    def test_add_ssh_key(self):
        user_id = 32
        ssh_key = "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAsEctmRR8YdO+nnZauPqhhsvOn6c30szVe1Gqmc6kM8/Wi9XS+dUKAL12iuQTrkuFCY6wvmfLG9ACIV8b1ZXxOxE3G5Q+0FvGJMHCdKL0b2fDCLiDNpcg22xOb4QaXggJaXR+M8yxNn5I+LIKpSA6vP6HEYKxm3aHQyrYDhy7WuJ8L/BUw+cAxDa0+y9l9ZuKwv5IdNTwU/WdQWeBXiLyhEV6Pcnx6pTDjgJqtnTHePQ/Cm/pedIYoeamFZwWkabnoTPZPiKa+ATLNXXOBzvcV32f2EFW7957TodpL1Yhg/WPDcD/2ypGWgmtUmWhYxJhXAactaTiZni+nhVjEi9zmQ=="
        description = "this is a test key"
        result = self.store.add_ssh_key(user_id, ssh_key, description)
        self.assertTrue(result)
        list = self.store.get_ssh_keys_by_user_id(user_id)
        count = len(list)
        self.assertEquals(count, 2) # one old, one new
        text = list[1].description
        self.assertEquals(text, "this is a test key")

    def test_add_ssh_key_error(self):
        user_id = 1000000 # should not exist in user.csv
        ssh_key = "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAsEctmRR8YdO+nnZauPqhhsvOn6c30szVe1Gqmc6kM8/Wi9XS+dUKAL12iuQTrkuFCY6wvmfLG9ACIV8b1ZXxOxE3G5Q+0FvGJMHCdKL0b2fDCLiDNpcg22xOb4QaXggJaXR+M8yxNn5I+LIKpSA6vP6HEYKxm3aHQyrYDhy7WuJ8L/BUw+cAxDa0+y9l9ZuKwv5IdNTwU/WdQWeBXiLyhEV6Pcnx6pTDjgJqtnTHePQ/Cm/pedIYoeamFZwWkabnoTPZPiKa+ATLNXXOBzvcV32f2EFW7957TodpL1Yhg/WPDcD/2ypGWgmtUmWhYxJhXAactaTiZni+nhVjEi9zmQ=="
        description = "this is a test key"
        result = self.store.add_ssh_key(user_id, ssh_key, description)
        self.assertFalse(result)
        list = self.store.get_ssh_keys_by_user_id(user_id)
        count = len(list)
        self.assertEquals(count, 0)     

    def test_remove_ssh_key(self):
        user_id = 34
        key_id = 19
        list = self.store.get_ssh_keys_by_user_id(user_id)
        count = len(list)
        self.assertEquals(count, 1)
        result = self.store.remove_ssh_key(user_id, key_id)
        self.assertTrue(result)
        list = self.store.get_ssh_keys_by_user_id(user_id)
        count = len(list)
        self.assertEquals(count, 0)
        result = self.store.remove_ssh_key(user_id, key_id)
        self.assertTrue(result)
        list = self.store.get_ssh_keys_by_user_id(user_id)
        count = len(list)
        self.assertEquals(count, 0)       
        
    def test_remove_ssh_key_error(self):
        user_id = 1000000 # should not exist in user.csv
        key_id = 19
        list = self.store.get_ssh_keys_by_user_id(user_id)
        count = len(list)
        self.assertEquals(count, 0)
        result = self.store.remove_ssh_key(user_id, key_id)
        self.assertTrue(result)
        user_id = None
        key_id = 19
        result = self.store.remove_ssh_key(user_id, key_id)
        self.assertFalse(result)
    
    def test_get_ssh_key_update_flags(self):
        list = self.store.get_ssh_key_update_flags()
        count = len(list)
        self.assertEquals(count, 1)   

    def test_clear_ssh_key_update_flags(self): 
        result = self.store.clean_ssh_key_update_flags()
        self.assertTrue(result)
        list = self.store.get_ssh_key_update_flags()
        count = len(list)
        self.assertEquals(count, 0)  
        result = self.store.clean_ssh_key_update_flags()
        self.assertTrue(result)
        list = self.store.get_ssh_key_update_flags()
        count = len(list)
        self.assertEquals(count, 0)           
     
    def test_add_ssh_key_update_flag(self):
        result = self.store.add_ssh_key_update_flag()
        self.assertTrue(result)
        list = self.store.get_ssh_key_update_flags()
        count = len(list)
        self.assertEquals(count, 1)
        result = self.store.add_ssh_key_update_flag()
        self.assertTrue(result)
        list = self.store.get_ssh_key_update_flags()
        count = len(list)
        self.assertEquals(count, 1) # only one flag should be raised
        
    def test_generate_ssh_key_file(self):
        tmp_dir = tempfile.mkdtemp('','tmp',self.tmp_root)
        user_name = "matti@testaaja.com"
        ssh_key = "keykeykey"
        result = self.store.generate_ssh_key_file(user_name, ssh_key, tmp_dir)
        self.assertTrue(result)
        file_path = tmp_dir + "/" + user_name + ".pub"
        result = os.path.exists(file_path)
        self.assertTrue(result)
        linestring = open(file_path, 'r').read()
        result = linestring == ssh_key
        self.assertTrue(result)

        
        tmp_dir = tempfile.mkdtemp('','tmp',self.tmp_root) + "/"
        user_name = "teppo@testaaja.com"
        ssh_key = "dummykey"
        result = self.store.generate_ssh_key_file(user_name, ssh_key, tmp_dir)
        self.assertTrue(result)
        file_path = tmp_dir + user_name + ".pub"
        result = os.path.exists(file_path)
        self.assertTrue(result)
        linestring = open(file_path, 'r').read()
        result = linestring == ssh_key
        self.assertTrue(result)  
        
    def test_generate_ssh_key_file_error(self):
        tmp_dir = tempfile.mkdtemp('','tmp',self.tmp_root)
        user_name = None
        ssh_key = "keykeykey"
        result = self.store.generate_ssh_key_file(user_name, ssh_key, tmp_dir)
        self.assertFalse(result)
        tmp_dir = tempfile.mkdtemp('','tmp',self.tmp_root)
        user_name = ""
        ssh_key = "keykeykey"
        result = self.store.generate_ssh_key_file(user_name, ssh_key, tmp_dir)
        self.assertFalse(result)
        tmp_dir = "/location/that/should/not/exist"
        user_name = "matti@testaaja.com"
        ssh_key = "keykeykey"
        result = self.store.generate_ssh_key_file(user_name, ssh_key, tmp_dir)
        self.assertFalse(result)
        
    def test_generate_all_ssh_keys(self):
        tmp_dir = tempfile.mkdtemp('','tmp',self.tmp_root)
        count = self.store.generate_all_ssh_key_files(tmp_dir)
        self.assertEquals(count, 2)
        count = self.store.generate_all_ssh_key_files(tmp_dir)
        self.assertEquals(count, 0)
        
        result = self.store.remove_ssh_key(34, 19)
        self.assertTrue(result)
        tmp_dir = tempfile.mkdtemp('','tmp',self.tmp_root)
        count = self.store.generate_all_ssh_key_files(tmp_dir)
        self.assertEquals(count, 1)
        
        result = self.store.remove_ssh_key(32, 5)
        self.assertTrue(result)
        tmp_dir = tempfile.mkdtemp('','tmp',self.tmp_root)
        count = self.store.generate_all_ssh_key_files(tmp_dir)
        self.assertEquals(count, 0)
        
        
    def test_generate_all_ssh_keys_error(self):   
        tmp_dir = None
        count = self.store.generate_all_ssh_key_files(tmp_dir)
        self.assertEquals(count, 0)
        tmp_dir = ""
        count = self.store.generate_all_ssh_key_files(tmp_dir)
        self.assertEquals(count, 0)

    def test_perform_ssh_key_update(self):
        tmp_dir = tempfile.mkdtemp('','tmp',self.tmp_root)
        new_dir = tmp_dir + "/keydir/"
        os.makedirs(new_dir)
        result = self.store.perform_ssh_key_update(tmp_dir)
        self.assertTrue(result)
        
    def test_perform_ssh_key_update_error(self):
        tmp_dir = tempfile.mkdtemp('','tmp',self.tmp_root) # "gitosis-export/keydir/" is not created
        result = self.store.perform_ssh_key_update(tmp_dir)
        self.assertFalse(result)
        
        tmp_dir = tempfile.mkdtemp('','tmp',self.tmp_root)
        new_dir = tmp_dir + "/keydir/"
        os.makedirs(new_dir)
        result = self.store.perform_ssh_key_update(tmp_dir)
        self.assertTrue(result)
        result = self.store.perform_ssh_key_update(tmp_dir)
        self.assertFalse(result) # directory no longer empty
