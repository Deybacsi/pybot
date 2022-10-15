def checkbalance(threadno):
    pybot_threads[threadno]["asset1balance"] = client.get_asset_balance(asset=pybot_threads[threadno]["asset1"])["free"]
    pybot_threads[threadno]["asset2balance"] = client.get_asset_balance(asset=pybot_threads[threadno]["asset2"])["free"]
    
