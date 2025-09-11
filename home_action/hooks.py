def set_default_home_action(env):
    """Postavi home action svim korisnicima u bazi."""
    action = env.ref("universal_request_manager.action_universal_request", raise_if_not_found=False)
    if not action:
        return
    users = env["res.users"].with_user(1).search([])  # 1 = SUPERUSER_ID
    users.write({"action_id": action.id})
