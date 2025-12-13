import asyncio,json
from crawl4ai import AsyncWebCrawler,CrawlerRunConfig,CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

async def main():
    # 模擬加密貨幣網頁
    html = """<html>
        <body>
            <div class='product-card'>
                <h2>電競筆電 - 高效能遊戲機</h2>
                <p>這款筆電配備最新的 RTX 4070 顯示卡，
                   搭配 Intel i9 處理器，適合專業遊戲玩家。</p>
                <div class='price-section'>
                    <span class='old-price'>原價 $1499.99</span>
                <span class='new-price'>特價 $1299.99</span>
                </div>
                <a href='https://example.com/gaming-laptop'>查看詳情</a>
            </div>
            <div class='product-card'>
                <h2>無線滑鼠 - 人體工學設計</h2>
                <p>符合人體工學的無線滑鼠，電池續航力長達 3 個月。</p>
                <div class='price-section'>
                    <span class='new-price'>$29.99</span>
                </div>
                <a href='https://example.com/wireless-mouse'>查看詳情</a>
            </div>
        </body>
    </html> 
    """

    schema ={
        "name":"3C電子產品",
        "baseSelector":"div.product-card",
        "fields":[
            {
                "name":"商品名稱",
                "selector":"h2",
                "type":"text"
            },
            {
                "name":"價格",
                "selector":"span.new-price",
                "type":"text"
            },
        ]
    }

    strategy = JsonCssExtractionStrategy(schema)

    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        extraction_strategy=strategy
        )
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=f"raw://{html}",
            config=run_config)
        data = json.loads(result.extracted_content)
        for item in data:
            print(f"商品名稱: {item['商品名稱']}")
            print(f"價格: {item['價格']}")
            print("=============")

if __name__ == "__main__":
    asyncio.run(main())