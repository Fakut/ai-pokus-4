# services/response_optimizer.py
"""
Optimalizace rychlosti odpovědí
- Streaming responses
- Prediktivní cache
- Paralelní zpracování
- Asynchronní zpracování
"""

import asyncio
import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Callable
import time


class ResponseOptimizer:
    """
    Optimalizuje rychlost odpovědí pomocí:
    - Cache pro časté dotazy
    - Streaming responses
    - Paralelní zpracování
    """
    
    def __init__(self, cache_ttl: int = 3600):
        """
        Args:
            cache_ttl: Time to live pro cache v sekundách (default 1 hodina)
        """
        self.cache_ttl = cache_ttl
        self.cache_dir = Path("data/response_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.cache_file = self.cache_dir / "response_cache.json"
        self.stats_file = self.cache_dir / "cache_stats.json"
        
        self.cache = self._load_cache()
        self.stats = self._load_stats()
        
        # Prediktivní cache pro časté dotazy
        self.frequent_queries = {}
    
    def _load_cache(self) -> Dict:
        """Načte cache z disku"""
        if self.cache_file.exists():
            try:
                cache = json.loads(self.cache_file.read_text())
                # Odstraň expirované položky
                current_time = datetime.now().isoformat()
                cache = {
                    k: v for k, v in cache.items()
                    if v.get('expires_at', '') > current_time
                }
                return cache
            except:
                return {}
        return {}
    
    def _load_stats(self) -> Dict:
        """Načte statistiky cache"""
        if self.stats_file.exists():
            try:
                return json.loads(self.stats_file.read_text())
            except:
                return {'hits': 0, 'misses': 0, 'total_time_saved': 0}
        return {'hits': 0, 'misses': 0, 'total_time_saved': 0}
    
    def _save_cache(self):
        """Uloží cache na disk"""
        self.cache_file.write_text(
            json.dumps(self.cache, indent=2, ensure_ascii=False)
        )
    
    def _save_stats(self):
        """Uloží statistiky"""
        self.stats_file.write_text(
            json.dumps(self.stats, indent=2, ensure_ascii=False)
        )
    
    def _hash_query(self, query: str, context: Dict = None) -> str:
        """
        Vytvoří hash pro query (pro cache key)
        
        Args:
            query: Uživatelský dotaz
            context: Kontext (optional)
            
        Returns:
            Hash string
        """
        # Normalize query
        normalized = query.lower().strip()
        
        # Přidej kontext pokud existuje
        if context:
            context_str = json.dumps(context, sort_keys=True)
            normalized += context_str
        
        # Hash
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def get_cached_response(self, query: str, context: Dict = None) -> Optional[str]:
        """
        Získá odpověď z cache pokud existuje
        
        Args:
            query: Uživatelský dotaz
            context: Kontext
            
        Returns:
            Cachovaná odpověď nebo None
        """
        cache_key = self._hash_query(query, context)
        
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            
            # Zkontroluj expiraci
            if cached['expires_at'] > datetime.now().isoformat():
                print(f"   ⚡ [Cache] HIT - saved ~{cached.get('avg_generation_time', 0.5):.2f}s")
                
                # Update stats
                self.stats['hits'] += 1
                self.stats['total_time_saved'] += cached.get('avg_generation_time', 0.5)
                self._save_stats()
                
                # Update hit count
                cached['hit_count'] = cached.get('hit_count', 0) + 1
                cached['last_hit'] = datetime.now().isoformat()
                self._save_cache()
                
                return cached['response']
        
        # Cache miss
        self.stats['misses'] += 1
        self._save_stats()
        print(f"   ⚡ [Cache] MISS")
        
        return None
    
    def cache_response(self, query: str, response: str, 
                      context: Dict = None, generation_time: float = 0.5):
        """
        Uloží odpověď do cache
        
        Args:
            query: Uživatelský dotaz
            response: AI odpověď
            context: Kontext
            generation_time: Čas generování odpovědi (sekundy)
        """
        cache_key = self._hash_query(query, context)
        
        expires_at = datetime.now() + timedelta(seconds=self.cache_ttl)
        
        self.cache[cache_key] = {
            'query': query,
            'response': response,
            'context': context,
            'cached_at': datetime.now().isoformat(),
            'expires_at': expires_at.isoformat(),
            'avg_generation_time': generation_time,
            'hit_count': 0
        }
        
        self._save_cache()
        print(f"   ⚡ [Cache] Stored response")
    
    def analyze_frequent_queries(self):
        """
        Analyzuje cache a identifikuje časté dotazy
        Pro prediktivní caching
        """
        # Seřaď podle hit_count
        frequent = sorted(
            self.cache.items(),
            key=lambda x: x[1].get('hit_count', 0),
            reverse=True
        )[:10]
        
        self.frequent_queries = {
            k: v for k, v in frequent if v.get('hit_count', 0) > 2
        }
        
        print(f"\n⚡ [Cache] Frequent queries: {len(self.frequent_queries)}")
        for key, data in list(self.frequent_queries.items())[:3]:
            print(f"   - {data['query'][:50]}... (hits: {data.get('hit_count', 0)})")
    
    async def parallel_process(self, tasks: list) -> list:
        """
        Paralelní zpracování úloh
        
        Args:
            tasks: List async funkcí k provedení
            
        Returns:
            List výsledků
        """
        print(f"   ⚡ [Parallel] Processing {len(tasks)} tasks")
        start_time = time.time()
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        elapsed = time.time() - start_time
        print(f"   ⚡ [Parallel] Completed in {elapsed:.2f}s")
        
        return results
    
    def stream_response(self, response_generator: Callable):
        """
        Streamuje odpověď místo čekání na kompletní generování
        
        Args:
            response_generator: Generator funkce pro streaming
            
        Yields:
            Chunks of response
        """
        print(f"   ⚡ [Streaming] Starting response stream")
        
        for chunk in response_generator():
            yield chunk
    
    def clear_expired_cache(self):
        """Vyčistí expirované položky z cache"""
        current_time = datetime.now().isoformat()
        original_size = len(self.cache)
        
        self.cache = {
            k: v for k, v in self.cache.items()
            if v.get('expires_at', '') > current_time
        }
        
        removed = original_size - len(self.cache)
        if removed > 0:
            print(f"   ⚡ [Cache] Removed {removed} expired entries")
            self._save_cache()
    
    def get_cache_stats(self) -> Dict:
        """Vrátí statistiky cache"""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'total_cached': len(self.cache),
            'cache_hits': self.stats['hits'],
            'cache_misses': self.stats['misses'],
            'hit_rate': f"{hit_rate:.1f}%",
            'total_time_saved': f"{self.stats['total_time_saved']:.1f}s",
            'frequent_queries': len(self.frequent_queries)
        }
    
    def optimize_query_processing(self, query: str, intent: str) -> Dict:
        """
        Optimalizuje zpracování dotazu podle intent
        Vrací doporučení pro rychlejší zpracování
        
        Args:
            query: Dotaz
            intent: Detekovaný intent
            
        Returns:
            Dict s optimalizačními doporučeními
        """
        recommendations = {
            'use_cache': False,
            'parallel_kb_lookup': False,
            'stream_response': False,
            'max_tokens': 45
        }
        
        # Pro jednoduché dotazy použij cache
        if intent in ['confirmation', 'rejection']:
            recommendations['use_cache'] = True
            recommendations['max_tokens'] = 30  # Kratší odpověď
        
        # Pro složitější dotazy stream response
        if intent in ['question', 'interest']:
            recommendations['stream_response'] = True
            recommendations['parallel_kb_lookup'] = True
        
        # Pro price queries - určitě cache (často se ptají)
        if intent == 'price':
            recommendations['use_cache'] = True
            recommendations['parallel_kb_lookup'] = True
        
        return recommendations
    
    def measure_performance(self, func: Callable, *args, **kwargs) -> tuple:
        """
        Měří výkon funkce
        
        Args:
            func: Funkce k měření
            *args, **kwargs: Argumenty funkce
            
        Returns:
            (result, elapsed_time)
        """
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        
        return result, elapsed
    
    def should_use_cache(self, query: str, intent: str) -> bool:
        """
        Rozhodne zda použít cache pro daný dotaz
        
        Args:
            query: Dotaz
            intent: Intent
            
        Returns:
            True pokud použít cache
        """
        # Krátké a časté dotazy - cache
        if len(query.split()) <= 5:
            return True
        
        # Specifické intenty - cache
        cache_intents = ['price', 'confirmation', 'rejection', 'availability']
        if intent in cache_intents:
            return True
        
        # Časté dotazy - cache
        query_hash = self._hash_query(query)
        if query_hash in self.frequent_queries:
            return True
        
        return False
