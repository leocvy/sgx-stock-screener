# Singapore Stock Screener with Technical Indicators
# Author: Intern Project for Lion Global Investors
# Date: August 2025

import yfinance as yf
import pandas as pd
import numpy as np
import warnings
from datetime import datetime, timedelta
import time

warnings.filterwarnings('ignore')

class SGXStockScreener:
    def __init__(self):
        # Major SGX stocks with their tickers (sample list)
        self.sgx_stocks = {
            'DBS Group Holdings': 'D05.SI',
            'OCBC Bank': 'O39.SI',
            'Frenken': 'E28.SI',
            'CSE Global': '544.SI',
            'DFIRG': 'D01.SI',
            'CapitaLand Investment': '9CI.SI',
            'Wilmar International': 'F34.SI',
            'Food Empire': 'F03.SI',
            'AEM': 'AWX.SI',
            'HongLeong Asia': 'H22.SI',
            'First Resources': 'EB5.SI',
            'SembCorp Industries': 'U96.SI',
            'Thai Beverage': 'Y92.SI',
            'Bumitama Agri': 'P8Z.SI',
            'UMS': '558.SI',
            'ST Engineering': 'S63.SI',
            'Ascendas REIT': 'A17U.SI',
            'SGX': 'S68.SI',
            'AIMS APAC REIT': 'O5RU.SI',
            'YZJ Shipbldg': 'BS6.SI'
        }
        
        self.results = []
    
    def calculate_rsi(self, prices, period=14):
        """Calculate Relative Strength Index"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            result = rsi.iloc[-1]
            return float(result) if not pd.isna(result) else 50.0
        except:
            return 50.0
    
    def calculate_moving_averages(self, prices):
        """Calculate moving averages"""
        try:
            ma20 = float(prices.rolling(window=20).mean().iloc[-1])
            ma50 = float(prices.rolling(window=50).mean().iloc[-1])
            current_price = float(prices.iloc[-1])
            
            return {
                'ma20': ma20,
                'ma50': ma50,
                'current_price': current_price,
                'price_above_ma20': current_price > ma20,
                'price_above_ma50': current_price > ma50,
                'ma20_above_ma50': ma20 > ma50
            }
        except:
            current_price = float(prices.iloc[-1])
            return {
                'ma20': current_price,
                'ma50': current_price,
                'current_price': current_price,
                'price_above_ma20': True,
                'price_above_ma50': True,
                'ma20_above_ma50': True
            }
    
    def calculate_momentum(self, prices):
        """Calculate price momentum over different periods"""
        try:
            current = float(prices.iloc[-1])
            
            mom_5d = ((current / float(prices.iloc[-5])) - 1) * 100 if len(prices) >= 5 else 0
            mom_20d = ((current / float(prices.iloc[-20])) - 1) * 100 if len(prices) >= 20 else 0
            mom_50d = ((current / float(prices.iloc[-50])) - 1) * 100 if len(prices) >= 50 else 0
            
            return {
                'momentum_5d': mom_5d,
                'momentum_20d': mom_20d,
                'momentum_50d': mom_50d
            }
        except:
            return {
                'momentum_5d': 0,
                'momentum_20d': 0,
                'momentum_50d': 0
            }
    
    def calculate_volume_analysis(self, volume):
        """Analyze volume trends"""
        try:
            avg_volume = float(volume.rolling(window=20).mean().iloc[-1])
            current_volume = float(volume.iloc[-1])
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            return {
                'avg_volume': avg_volume,
                'current_volume': current_volume,
                'volume_ratio': volume_ratio,
                'high_volume': volume_ratio > 1.5
            }
        except:
            return {
                'avg_volume': 1000000,
                'current_volume': 1000000,
                'volume_ratio': 1.0,
                'high_volume': False
            }
    
    def calculate_score(self, indicators):
        """Calculate overall stock score (0-100)"""
        score = 0
        
        # RSI scoring (30-70 is good range)
        rsi = indicators['rsi']
        if 30 <= rsi <= 70:
            score += 20
        elif rsi < 30:  # Oversold might be opportunity
            score += 15
        else:  # Overbought
            score += 5
        
        # Moving average scoring
        if indicators['price_above_ma20']:
            score += 15
        if indicators['price_above_ma50']:
            score += 15
        if indicators['ma20_above_ma50']:
            score += 10
        
        # Momentum scoring
        mom_20d = indicators['momentum_20d']
        if mom_20d > 5:
            score += 15
        elif mom_20d > 0:
            score += 10
        elif mom_20d > -5:
            score += 5
        
        # Volume scoring
        if indicators['high_volume'] and indicators['momentum_5d'] > 0:
            score += 10
        elif indicators['volume_ratio'] > 1.2:
            score += 5
        
        # Volatility bonus (moderate volatility preferred)
        if 2 <= abs(indicators['momentum_5d']) <= 8:
            score += 15
        
        return min(score, 100)  # Cap at 100
    
    def analyze_stock(self, symbol, name):
        """Analyze a single stock"""
        try:
            print(f"Analyzing {name} ({symbol})...")
            
            # Download 3 months of data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            
            stock = yf.download(symbol, start=start_date, end=end_date, progress=False)
            
            if stock.empty or len(stock) < 20:
                print(f"Insufficient data for {name}")
                return None
            
            # Calculate indicators
            prices = stock['Close']
            volume = stock['Volume']
            
            rsi = self.calculate_rsi(prices)
            ma_data = self.calculate_moving_averages(prices)
            momentum = self.calculate_momentum(prices)
            volume_data = self.calculate_volume_analysis(volume)
            
            # Combine all indicators
            indicators = {
                'symbol': symbol,
                'name': name,
                'current_price': ma_data['current_price'],
                'rsi': rsi,
                'ma20': ma_data['ma20'],
                'ma50': ma_data['ma50'],
                'price_above_ma20': ma_data['price_above_ma20'],
                'price_above_ma50': ma_data['price_above_ma50'],
                'ma20_above_ma50': ma_data['ma20_above_ma50'],
                'momentum_5d': momentum['momentum_5d'],
                'momentum_20d': momentum['momentum_20d'],
                'momentum_50d': momentum['momentum_50d'],
                'volume_ratio': volume_data['volume_ratio'],
                'high_volume': volume_data['high_volume']
            }
            
            # Calculate overall score
            indicators['score'] = self.calculate_score(indicators)
            
            return indicators
            
        except Exception as e:
            print(f"Error analyzing {name}: {str(e)}")
            return None
    
    def screen_stocks(self):
        """Screen all stocks and return results"""
        print("Starting SGX Stock Screening...")
        print("=" * 50)
        
        for name, symbol in self.sgx_stocks.items():
            result = self.analyze_stock(symbol, name)
            if result:
                self.results.append(result)
            
            # Small delay to avoid overwhelming the API
            time.sleep(0.5)
        
        # Sort by score (highest first)
        self.results = sorted(self.results, key=lambda x: x['score'], reverse=True)
        
        return self.results
    
    def create_report(self):
        """Create and save screening report"""
        if not self.results:
            print("No results to report")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(self.results)
        
        # Select and rename columns for report
        report_df = df[[
            'name', 'symbol', 'current_price', 'score', 'rsi',
            'momentum_5d', 'momentum_20d', 'momentum_50d',
            'price_above_ma20', 'price_above_ma50', 'volume_ratio'
        ]].copy()
        
        report_df.columns = [
            'Company', 'Symbol', 'Price (SGD)', 'Score', 'RSI',
            '5D Momentum (%)', '20D Momentum (%)', '50D Momentum (%)',
            'Above MA20', 'Above MA50', 'Volume Ratio'
        ]
        
        # Round numerical columns
        report_df['Price (SGD)'] = report_df['Price (SGD)'].round(2)
        report_df['RSI'] = report_df['RSI'].round(1)
        report_df['5D Momentum (%)'] = report_df['5D Momentum (%)'].round(1)
        report_df['20D Momentum (%)'] = report_df['20D Momentum (%)'].round(1)
        report_df['50D Momentum (%)'] = report_df['50D Momentum (%)'].round(1)
        report_df['Volume Ratio'] = report_df['Volume Ratio'].round(2)
        
        # Save to Excel
        # Create reports directory if it doesn't exist
        os.makedirs('reports', exist_ok=True)

        filename = f'reports/SGX_Stock_Screen_{datetime.now().strftime("%Y%m%d")}.xlsx'
        report_df.to_excel(filename, index=False)
        
        print(f"\nReport saved as: {filename}")
        print("\nTop 5 Stocks by Score:")
        print("=" * 50)
        
        for i, row in report_df.head().iterrows():
            print(f"{i+1}. {row['Company']} ({row['Symbol']})")
            print(f"   Score: {row['Score']}/100 | Price: ${row['Price (SGD)']} | RSI: {row['RSI']}")
            print(f"   20D Momentum: {row['20D Momentum (%)']}% | Volume Ratio: {row['Volume Ratio']}")
            print()
        
        return report_df

def main():
    """Main execution function"""
    print("SGX Stock Screener")
    print("Developed for Lion Global Investors Internship")
    print("=" * 60)
    
    screener = SGXStockScreener()
    
    # Screen all stocks
    results = screener.screen_stocks()
    
    if results:
        print(f"\nSuccessfully analyzed {len(results)} stocks")
        
        # Create and display report
        report = screener.create_report()
        
        print("\nScreening Complete!")
        print("Check the generated Excel file for detailed results.")
    else:
        print("No stocks were successfully analyzed.")

if __name__ == "__main__":
    main()
