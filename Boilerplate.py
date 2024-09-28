from itertools import combinations_with_replacement
import math
import catPyNet.main.CatPyNet as cpn
def main():
    
    alph = ['a', 'b']
    for i in range(11):
        print("Length of a=" + str(len(alph)) + "k=" + str(i)+ " " + str(len(list(combinations_with_replacement(alph, i)))))
        print(str(sum([j for j in  range(len(alph) + i)])))

def get_org(pathway_code:str, org_code:str, output_path:str):
    import requests
    import time
    pathway_list = []
    with open("G:\\Github\\BA-Jan\\test_files\\eco00010             Glycolysis  Gl.txt", 'r') as f:
        lines = f.readlines()
        for line in lines:
            pathway_list.append(line.split()[0].strip())
    
    reactions = []
    all_modules = []
    for pathway_code in pathway_list:
        url = f'https://rest.kegg.jp/get/{pathway_code}'
        response = requests.get(url)
        time.sleep(0.334)    
        if response.status_code == 200:
            pathways_str = response.text
            modules = []
            for pthw_line in pathways_str.splitlines():
                if pthw_line.startswith('MODULE'):
                    modules.append(pthw_line.removeprefix('MODULE').split()[0].strip())
                elif pthw_line.strip().startswith(org_code + '_M'):
                    modules.append(pthw_line.split()[0].strip())
            reaction_strs = set()
            for mod in modules:
                mod = mod.removeprefix(org_code + '_')
                if mod in all_modules: continue
                all_modules.append(mod)
                print(mod)
                url = f'https://rest.kegg.jp/get/{mod}'
                response = requests.get(url)
                time.sleep(0.334)
                mod_lines = response.text.splitlines()
                reaction_bool = False
                for mod_line in mod_lines:
                    if mod_line.startswith('REACTION'):
                        reaction_bool = True
                    elif mod_line.startswith('COMPOUND'):
                        break
                    if reaction_bool:
                        mod_line = mod_line.removeprefix('REACTION').strip()
                        try: reaction_str = mod_line.split()[0].strip()
                        except: continue
                        sub_reaction_strs = []
                        if ',' in reaction_str:
                            sub_reaction_strs.extend(reaction_str.split(','))
                        if not sub_reaction_strs:
                            reaction_strs.update([reaction_str])
            for reaction_str in reaction_strs:
                if reaction_str in [react[0] for react in reactions]: continue
                url = f'https://rest.kegg.jp/get/{reaction_str}'
                response = requests.get(url)
                time.sleep(0.334)
                reac_lines = response.text.splitlines()
                reaction = [reaction_str, "",[]]
                for reac_line in reac_lines:
                    if reac_line.startswith('EQUATION'):
                        reaction[1] = reac_line.removeprefix('EQUATION').strip()
                    elif reac_line.startswith('ENZYME'):
                        reaction[2] = [enz.strip() for enz in reac_line.split()[1:]]
                        break
                print(str(reaction))
                reactions.append(reaction)
                """ for enzymes in [reaction[1] for reaction in reactions]:
                    for enzyme in enzymes:
                        enz_url = f'https://rest.kegg.jp/get/{enzyme}'
                        response = requests.get(enz_url)
                        time.sleep(0.334)
                        print(response.text) """     
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
    if reactions:
        reaction_obj_lst:list[Reaction] = []
        from catPyNet.model.ReactionSystem import Reaction, ReactionSystem
        for i, reaction in enumerate(reactions):
            reaction_obj_lst.insert(i, Reaction().parse_new(" : ".join([reaction[0], reaction[1]]),False))
            reaction_obj_lst[i].catalysts = ",".join(reaction[2])
        output_rs = ReactionSystem(reactions=reaction_obj_lst)
        cpn.export_rs_to_output_file([output_rs], output_path)
        total_res_rs = cpn.parse_input_file_to_rs("G:\\Github\\BA-Jan\\test_results\\test_reactions.crs")
        shared_reactions = set(total_res_rs.reactions).intersection(output_rs.reactions)
        output_rs = shared_reactions
        cpn.export_rs_to_output_file([output_rs], "G:\\Github\\BA-Jan\\test_results\e_coli_rs_shared.crs")
    else: print('no reactions')
            

def compare_files():
    sys_1 = cpn.parse_input_file_to_rs("G:\\Github\\BA-Jan\\test_results\\test_reactions.crs")
    sys_2 = cpn.parse_input_file_to_rs("G:\\Github\\BA-Jan\\test_results\\e_coli_rs.crs")
    shared_reactions = set([reaction.name for reaction in sys_2.reactions]).intersection([reaction.name for reaction in sys_1.reactions])
    print([reaction.name for reaction in sys_2.reactions])
    print([reaction.name for reaction in sys_1.reactions])
    print([reaction for reaction in shared_reactions])
    #sys_1.reactions = shared_reactions
    cpn.export_rs_to_output_file(sys_1, "G:\\Github\\BA-Jan\\test_results\e_coli_rs_shared.crs")
    
if __name__ == "__main__":
    import requests
    enzyme = '5.3.1.1'
    enz_url = f'https://rest.kegg.jp/link/reaction/eco'
    response = requests.get(enz_url)
    print(response.status_code)
    #get_org(pathway_code= 'eco01100', org_code='eco', output_path="G:\\Github\\BA-Jan\\test_results\e_coli_rs.crs")
    #compare_files()