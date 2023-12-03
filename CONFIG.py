from widgets import RadioButton, Val

CONFIG = {
    "FPS_CAP": 10,
    "GENERATOR": Val("random_dfs"),
    "ALGOS": ["random_dfs", "prim"],
    "SOLVER": Val("breadth_first_search"),
    "SOLVER_ALGOS": ["breadth_first_search", "depth_first_search", "a_star" ]
}

def curried_select(config_key:str, ):
    def set_group(radiobuttons:list[RadioButton]):
        def set_choice(choice):
            def execute():
                CONFIG[config_key].set(choice)
                print(CONFIG[config_key].value)
                for btn in radiobuttons:
                    btn.checked = btn.assigned == choice
            return execute
        return set_choice
    return set_group
