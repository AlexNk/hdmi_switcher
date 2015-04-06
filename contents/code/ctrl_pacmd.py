# -*- coding: utf-8 -*-
#!/usr/bin/python

import subprocess
import re

class ctrl:
    def __init__(self):
        self.expr_idx  = re.compile("\n[\s]+name: <([^<>]+)>\n")
        self.expr_name = re.compile("\n[\s]+alsa\.card_name = \"([^\n]+)\"\n")
        self.expr_out  = re.compile("(\n[\s]+(output:[^\n]+): ([^\n:]+) \([^\(\)]+\))")
        self.expr_prof = re.compile("active profile: <([^<>]+)>")
        
    def run_cmd(self, params):
        try:
            out, err = subprocess.Popen(["pacmd"] + params, stdout=subprocess.PIPE).communicate()
            return out
        except Exception as e:
            print(str(e));

    def list_cards(self):
        cards = []
        out = self.run_cmd(["list-cards"])
        if (out != None):
            while True:
                pos = out.rfind("\n    index: ")
                if (pos == -1): break
                cards.append(out[pos:])
                out = out[:pos]
            cards.reverse()

        ret = {}
        for card in cards:
            g_id = self.expr_idx.search(card)
            g_name = self.expr_name.search(card)
            g_prof = self.expr_prof.search(card)
            if (g_id != None) and (g_name != None):
                id = g_id.group(1)
                ret[id] = {}
                ret[id]["name"] = g_name.group(1) if g_name else ""
                ret[id]["active_profile"] = g_prof.group(1) if g_prof else ""
                ret[id]["profiles"] = []
                for i in self.expr_out.finditer(card):
                    profile = {"id":i.group(2), "name":i.group(3)}
                    ret[id]["profiles"].append(profile)
        return ret

    def select_profile(self, card_id, profile_id):
        self.run_cmd(["set-card-profile", card_id, profile_id])

    def get_active_profile(self, card_id):
        cards = self.list_cards()
        if card_id not in cards:
            return None
        return cards[card_id]["active_profile"]
