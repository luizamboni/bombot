import yaml
from yaml.loader import SafeLoader
import re

def interpolate_text(text, variables, functions):
    if not text:
        return None

    interpolated_text = text

    slots = re.findall("\{.*?\}", interpolated_text)
    for slot in slots:
        slot_key = slot[1:-1]
        template_function = functions.get(slot_key, None)
        if template_function:
            if not template_function.startswith("def"):
                slot_value = eval(template_function)
            else:
                slot_value = "undef"
        else:
            slot_value = variables[slot_key]
    
        interpolated_text = interpolated_text.replace(slot, str(slot_value))
    return interpolated_text

class UnexpectedResponse(Exception):
    pass


class Conversation:

    def _load_script(self, script_name):
        file = f"./dialogs/{script_name}/script.yml"
        with open(file) as f:
            self.script = yaml.load(f, Loader=SafeLoader)

    def __init__(self, script_name, data):

        self.index = "start"
        self.data = data
        self._load_script(script_name)


    def handle_response(self, response_text):
        section = self.get_section()
        response_matched = False
        if response_text in section["awnsers"]:
            self.set_index(response_text)
            response_matched = True

        if section["state"]:
            try: 
                state = response_text
                for filter in section.get("state_filters"):
                    state = eval(filter)

                self.data[section["state"]] = state
            except:
                raise UnexpectedResponse("not handled response")

        if section["next"]:                
            if section["next"].startswith("dialogs:"):
                script_name = section["next"][8:]
                self._load_script(script_name)
                self.set_index("start")
                response_matched = True
            else:
                self.set_index(section["next"])
                response_matched = True

        return response_matched
    
    def set_index(self, new_index):
        if new_index.startswith("dialogs:"):
            script_name = new_index[8:]
            self._load_script(script_name)
            self.index = "start"
        else:
            self.index = new_index
    
    def get_section(self):
        section = self.script[self.index]
        section_functions = section.get("functions", {})
        parsed_section = {
            "functions": section.get("functions", []),
            "talks": list(map(lambda v: interpolate_text(v, self.data, section_functions), section.get("talks", []))),
            "question": interpolate_text(section.get("question", None), self.data, section_functions),
            "awnsers": list(map(lambda v: interpolate_text(v, self.data, section_functions), section.get("awnsers", []))),
            "next": section.get("next", None),
            "state_filters": section.get("state_filters", []),
            "state": section.get("state", None),
        }

        return parsed_section

    def get_sections(self):
        sections = []
        
        current_section = self.get_section()

        sections.append(current_section)
        while not current_section["question"] and current_section["next"]:
            self.set_index(current_section["next"])
            current_section = self.get_section()
            sections.append(current_section)

        return sections

    def get_data(self):
        return self.data