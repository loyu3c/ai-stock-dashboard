from data_fetcher import DataFetcher
import time

def benchmark_scan():
    fetcher = DataFetcher()
    api = fetcher.api
    
    print("🚀 Benchmarking Full Market Scan...")
    start = time.time()
    
    # 1. Get Candidates
    candidates = []
    
    # TSE
    for c in api.Contracts.Stocks.TSE:
        if c.security_type == 'STK' and len(c.code) == 4:
            candidates.append(c)
            
    # OTC
    for c in api.Contracts.Stocks.OTC:
        if c.security_type == 'STK' and len(c.code) == 4:
            candidates.append(c)
            
    print(f"✅ Found {len(candidates)} candidates. (Time: {time.time() - start:.2f}s)")
    
    # 2. Snapshot (Batch)
    snap_start = time.time()
    snapshots = []
    batch_size = 500
    
    for i in range(0, len(candidates), batch_size):
        batch = candidates[i:i+batch_size]
        try:
            snaps = api.snapshots(batch)
            snapshots.extend(snaps)
            print(f"   Fetched batch {i}...")
        except Exception as e:
            print(f"❌ Batch {i} failed: {e}")
            
    print(f"📸 Snapshots done. (Time: {time.time() - snap_start:.2f}s)")
    
    # 3. Sort
    snapshots.sort(key=lambda s: s.total_volume, reverse=True)
    
    print("\n🏆 Top 5:")
    for s in snapshots[:5]:
        print(f"{s.code} Vol:{s.total_volume} Close:{s.close}")
        
    total_time = time.time() - start
    print(f"\n🏁 Total Time: {total_time:.2f}s")

if __name__ == "__main__":
    benchmark_scan()
