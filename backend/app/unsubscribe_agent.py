from playwright.async_api import async_playwright, Page, Browser
from typing import Optional
import asyncio
import re


class UnsubscribeAgent:
    """
    AI-powered agent to automatically unsubscribe from email lists
    Uses Playwright to navigate and interact with unsubscribe pages
    """
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.playwright = None
    
    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def unsubscribe(self, unsubscribe_url: str) -> dict:
        """
        Attempt to unsubscribe from an email list
        Returns dict with success status and message
        """
        if not self.browser:
            return {"success": False, "message": "Browser not initialized"}
        
        if not unsubscribe_url:
            return {"success": False, "message": "No unsubscribe URL provided"}
        
        try:
            page = await self.browser.new_page()
            await page.goto(unsubscribe_url, wait_until='networkidle', timeout=15000)
            
            # Wait a moment for page to fully load
            await asyncio.sleep(1)
            
            # Try different unsubscribe patterns
            result = await self._try_unsubscribe_patterns(page)
            
            await page.close()
            return result
            
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    async def _try_unsubscribe_patterns(self, page: Page) -> dict:
        """
        Try various patterns to detect and click unsubscribe buttons/links
        """
        # Pattern 1: Look for unsubscribe buttons
        unsubscribe_selectors = [
            'button:has-text("unsubscribe")',
            'a:has-text("unsubscribe")',
            'input[type="submit"][value*="unsubscribe"]',
            'button:has-text("Unsubscribe")',
            'a:has-text("Unsubscribe")',
            'button:has-text("Opt out")',
            'a:has-text("Opt out")',
            'button:has-text("Remove")',
            'a:has-text("Remove me")',
            '[class*="unsubscribe"]',
            '[id*="unsubscribe"]',
        ]
        
        for selector in unsubscribe_selectors:
            try:
                element = page.locator(selector).first
                if await element.count() > 0:
                    await element.click(timeout=5000)
                    await asyncio.sleep(2)
                    
                    # Check for confirmation
                    confirmation = await self._check_confirmation(page)
                    if confirmation:
                        return {"success": True, "message": "Successfully unsubscribed"}
                    
                    # Try to find and click confirm button
                    confirm_selectors = [
                        'button:has-text("confirm")',
                        'button:has-text("yes")',
                        'button:has-text("submit")',
                        'input[type="submit"]',
                    ]
                    
                    for confirm_selector in confirm_selectors:
                        confirm_element = page.locator(confirm_selector).first
                        if await confirm_element.count() > 0:
                            await confirm_element.click(timeout=5000)
                            await asyncio.sleep(2)
                            
                            confirmation = await self._check_confirmation(page)
                            if confirmation:
                                return {"success": True, "message": "Successfully unsubscribed"}
            except:
                continue
        
        # Pattern 2: Look for forms with email input
        try:
            # Check if there's a form with email field
            email_inputs = page.locator('input[type="email"], input[name*="email"]')
            if await email_inputs.count() > 0:
                # This might be a confirmation form, look for submit button
                submit_buttons = page.locator('button[type="submit"], input[type="submit"]')
                if await submit_buttons.count() > 0:
                    await submit_buttons.first.click(timeout=5000)
                    await asyncio.sleep(2)
                    
                    confirmation = await self._check_confirmation(page)
                    if confirmation:
                        return {"success": True, "message": "Successfully unsubscribed"}
        except:
            pass
        
        # Pattern 3: Check if already unsubscribed (page text)
        try:
            page_content = await page.content()
            text_content = await page.inner_text('body')
            
            success_patterns = [
                r'successfully unsubscribed',
                r'you have been unsubscribed',
                r'removed from.*list',
                r'no longer receive',
                r"won't receive",
                r'unsubscribe successful',
                r'preferences updated',
                r'email preferences saved'
            ]
            
            for pattern in success_patterns:
                if re.search(pattern, text_content, re.IGNORECASE):
                    return {"success": True, "message": "Unsubscribe confirmed"}
        except:
            pass
        
        return {"success": False, "message": "Could not find unsubscribe button or form"}
    
    async def _check_confirmation(self, page: Page) -> bool:
        """Check if unsubscribe was successful based on page content"""
        try:
            text_content = await page.inner_text('body')
            
            success_patterns = [
                r'successfully unsubscribed',
                r'you have been unsubscribed',
                r'removed from.*list',
                r'no longer receive',
                r"won't receive",
                r'unsubscribe successful',
                r'preferences updated',
                r'email preferences saved'
            ]
            
            for pattern in success_patterns:
                if re.search(pattern, text_content, re.IGNORECASE):
                    return True
        except:
            pass
        
        return False


async def unsubscribe_from_email(unsubscribe_url: str) -> dict:
    """
    Convenience function to unsubscribe from an email
    """
    async with UnsubscribeAgent() as agent:
        return await agent.unsubscribe(unsubscribe_url)

