def get_activity_info(all_tasks, task_id, forward_mode: bool =True, max_id_to_test: int = 5):
    for id_diff in range(max_id_to_test):
        if forward_mode:
            proc_id = task_id + id_diff
        else:
            proc_id = task_id - id_diff

        if all_tasks[proc_id]["type"] == "activity":
            return all_tasks[proc_id]
