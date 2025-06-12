import asyncio
from playwright.async_api import async_playwright
import time
import os
from pathlib import Path
import json
import aiohttp

# 用于控制浏览器关闭的事件
close_event = None

async def get_current_block_height():
    """使用API获取当前区块高度"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://mempool.space/api/blocks/tip/height') as response:
                if response.status == 200:
                    height = await response.text()
                    return int(height)
                else:
                    print(f"API请求失败，状态码: {response.status}")
                    return None
    except Exception as e:
        print(f"获取区块高度时出错: {str(e)}")
        return None

async def wait_for_block_height(target_height):
    """等待直到达到目标区块高度"""
    print(f"等待区块高度达到: {target_height}")
    
    while True:
        current_height = await get_current_block_height()
        if current_height is not None:
            print(f"当前区块高度: {current_height}")
            if current_height >= target_height:
                print(f"已达到目标区块高度！")
                return True
        await asyncio.sleep(5)  # 每5秒检查一次

def read_wallet_file(file_path):
    """读取钱包文件，返回钱包地址和私钥的列表"""
    wallet_info = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():  # 跳过空行
                    parts = line.strip().split('----')
                    if len(parts) == 2:
                        wallet_address = parts[0]
                        private_key = parts[1]
                        wallet_info.append((wallet_address, private_key))
        return wallet_info
    except Exception as e:
        print(f"读取钱包文件时出错: {str(e)}")
        return []

async def wait_for_user_input():
    """等待用户按下回车键"""
    print("\n所有操作已完成。按回车键关闭所有浏览器...")
    await asyncio.get_event_loop().run_in_executor(None, input)
    close_event.set()

async def wait_for_page_load(page, browser_id):
    """等待页面完全加载"""
    try:
        # 等待页面加载完成
        await page.wait_for_load_state('networkidle', timeout=30000)
        # 等待关键元素出现
        await page.wait_for_selector('#singleReceiveAddress', timeout=30000)
        await page.wait_for_selector('#wif', timeout=30000)
        await page.wait_for_selector('#custom', timeout=30000)
        await page.wait_for_selector('#feeRate', timeout=30000)
        await page.wait_for_selector('#maxFee', timeout=30000)
        print(f"浏览器 {browser_id} 页面已完全加载")
        # 额外等待一秒，确保页面完全稳定
        await asyncio.sleep(1)
        return True
    except Exception as e:
        print(f"浏览器 {browser_id} 等待页面加载时出错: {str(e)}")
        return False

async def control_browser(browser_id, url, wallet_info, fee_rate=6, max_fee=8):
    """控制单个浏览器的函数"""
    wallet_address, private_key = wallet_info
    
    try:
        async with async_playwright() as p:
            # 启动浏览器
            browser = await p.chromium.launch(
                headless=False,  # 设置为 False 可以看到浏览器界面
            )
            
            # 创建新的上下文
            context = await browser.new_context(
                viewport=None,  # 禁用视口大小限制
                accept_downloads=True,  # 允许下载
                ignore_https_errors=True  # 忽略 HTTPS 错误
            )
            
            # 创建新的页面
            page = await context.new_page()
            print(f"浏览器 {browser_id} 已启动")
            
            # 导航到指定URL
            await page.goto(url, wait_until='networkidle')
            print(f"浏览器 {browser_id} 已打开页面: {url}")
            
            # 等待页面完全加载
            if not await wait_for_page_load(page, browser_id):
                print(f"浏览器 {browser_id} 页面加载超时，跳过后续操作")
                return
            
            # 执行输入操作
            try:

                # 输入私钥
                await page.fill('#wif', private_key)
                print(f"浏览器 {browser_id} 已输入私钥")
                await asyncio.sleep(0.8)  # 短暂等待确保输入完成

                # 清空并输入钱包地址
                address_input = await page.query_selector('#singleReceiveAddress')
                await address_input.click()
                await page.keyboard.press('Control+A')
                await page.keyboard.press('Delete')
                await asyncio.sleep(0.2)  # 短暂等待确保清空完成
                await address_input.fill(wallet_address)
                print(f"浏览器 {browser_id} 已输入钱包地址: {wallet_address}")
                await asyncio.sleep(0.5)  # 短暂等待确保输入完成
                
                
                # 点击自定义按钮
                await page.click('#custom')
                print(f"浏览器 {browser_id} 已点击自定义按钮")
                await asyncio.sleep(0.5)  # 短暂等待确保点击生效
                
                # 清空并输入 gas 费率
                fee_input = await page.query_selector('#feeRate')
                await fee_input.click()
                await page.keyboard.press('Control+A')
                await page.keyboard.press('Delete')
                await asyncio.sleep(0.2)  # 短暂等待确保清空完成
                await fee_input.fill(str(fee_rate))
                print(f"浏览器 {browser_id} 已输入 gas 费率: {fee_rate}")
                await asyncio.sleep(0.5)  # 短暂等待确保输入完成
                
                # 清空并输入最大 gas 费率
                max_fee_input = await page.query_selector('#maxFee')
                await max_fee_input.click()
                await page.keyboard.press('Control+A')
                await page.keyboard.press('Delete')
                await asyncio.sleep(0.2)  # 短暂等待确保清空完成
                await max_fee_input.fill(str(max_fee))
                print(f"浏览器 {browser_id} 已输入最大 gas 费率: {max_fee}")
                await asyncio.sleep(0.5)  # 短暂等待确保输入完成

                # 等待开始铸造按钮可点击并点击
                start_button = await page.wait_for_selector('#startMinting', timeout=10000)
                await asyncio.sleep(1)  # 等待一秒确保所有输入都已经生效
                await start_button.click()
                print(f"浏览器 {browser_id} 已点击开始铸造按钮")
                
                # 等待并点击确认按钮
                # confirm_button = await page.wait_for_selector('#confirmMintButton', timeout=10000)
                # await asyncio.sleep(1)  # 等待一秒确保按钮可点击
                # await confirm_button.click()
                # print(f"浏览器 {browser_id} 已点击确认按钮")
                
            except Exception as e:
                print(f"浏览器 {browser_id} 输入信息或点击按钮时出错: {str(e)}")
            
            # 获取页面标题
            title = await page.title()
            print(f"浏览器 {browser_id} 页面标题: {title}")
            
            # 等待用户手动关闭信号
            await close_event.wait()
            
            # 关闭浏览器
            await browser.close()
            print(f"浏览器 {browser_id} 已关闭")
            
    except Exception as e:
        print(f"浏览器 {browser_id} 发生错误: {str(e)}")

async def main():
    global close_event
    close_event = asyncio.Event()
    
    # 设置目标区块高度
    target_height = 900868
    
    # 等待达到目标区块高度
    await wait_for_block_height(target_height)
    
    # 读取钱包文件
    wallet_info_list = read_wallet_file('sign-wallet.txt')
    
    if not wallet_info_list:
        print("没有找到有效的钱包信息，请检查 sign-wallet.txt 文件")
        return
    
    print(f"找到 {len(wallet_info_list)} 个钱包信息")
    
    # 要访问的网址
    base_url = "https://alkanes.ybot.io/?runeid=2:21568"
    
    # 设置 gas 费率
    fee_rate = 6  # 自定义的 gas 费率
    max_fee = 10  # 最大 gas 费率
    
    # 创建与钱包数量相同的浏览器任务
    browser_tasks = []
    for i, wallet_info in enumerate(wallet_info_list, 1):
        task = control_browser(i, base_url, wallet_info, fee_rate, max_fee)
        browser_tasks.append(task)
    
    # 创建等待用户输入的任务
    input_task = wait_for_user_input()
    
    # 并发执行所有任务
    print("开始启动所有浏览器...")
    await asyncio.gather(input_task, *browser_tasks)
    print("所有浏览器已关闭！")

if __name__ == "__main__":
    # 运行主程序
    asyncio.run(main()) 