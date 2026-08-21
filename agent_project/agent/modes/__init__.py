from .cot import cot_prompt
from .few_shot import few_shot_prompt
from .react import react_prompt
from .tot import tot_solve

BUILDERS = {
    "cot": cot_prompt,
    "few_shot": few_shot_prompt,
    "react": react_prompt,
    "tot": tot_solve,
}