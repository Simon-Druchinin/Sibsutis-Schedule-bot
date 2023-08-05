from yoomoney import Authorize

Authorize(
      client_id="67BE0D32EA8D7C4E332DE8CDAEC3D3FBB97321FC27320DBC0380F305728A9FF5",
      redirect_uri="https://t.me/SibsutisScheduleBot",
      scope=["account-info",
             "operation-history",
             "operation-details",
             "incoming-transfers",
             "payment-p2p",
             "payment-shop",
             ]
      )