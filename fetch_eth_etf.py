import requests
import pandas as pd
import json

def fetch_eth_etf_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    
    print("🔍 放弃模糊搜索，正在通过精准 Slug 直接定位以太坊 ETF 市场...")
    # 绝杀：直接用 URL Slug 精准锁定，不管它搜索算法怎么变
    url = "https://gamma-api.polymarket.com/events?slug=ethereum-etf-approved-by-may-31"
    
    try:
        r = requests.get(url, headers=headers)
        events = r.json()
        
        if not events:
            print("❌ 找不到对应的市场事件。")
            return
            
        event = events[0]
        title = event.get('title', 'Unknown Title')
        
        # 【排雷核心操作】
        # 应对 Polymarket API 糟糕的格式一致性问题
        raw_tokens = event['markets'][0]['clobTokenIds']
        if isinstance(raw_tokens, str):
            # 如果是假装成列表的字符串 '["0x..."]'，就将其反序列化为真列表
            tokens = json.loads(raw_tokens)
        else:
            tokens = raw_tokens
            
        target_token_id = tokens[0]
        
        print(f"✅ 精准锁定目标市场: {title}")
        print(f"🔑 成功提取真实的 Token ID: {target_token_id}")
        print("-" * 40)
        
        print("📡 正在抓取该市场的全年日线数据 (fidelity=1440)...")
        history_url = "https://clob.polymarket.com/prices-history"
        params = {
            "market": target_token_id,
            "interval": "max",
            "fidelity": 1440 
        }
        
        r2 = requests.get(history_url, params=params, headers=headers)
        data = r2.json()
        
        if "history" in data and len(data["history"]) > 0:
            df = pd.DataFrame(data["history"])
            df['date'] = pd.to_datetime(df['t'], unit='s').dt.strftime('%Y-%m-%d')
            df = df.rename(columns={'p': 'price'})
            df_final = df[['date', 'price']]
            
            filename = "eth_etf_history.csv"
            df_final.to_csv(filename, index=False)
            print(f"🎉 大功告成！以太坊 ETF 历史数据已完美保存至: {filename}")
        else:
            print("⚠️ 数据为空，请检查网络。")

    except Exception as e:
        print(f"❌ 运行出错: {e}")

if __name__ == "__main__":
    fetch_eth_etf_data()