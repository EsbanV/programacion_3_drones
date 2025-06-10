from typing import List, Dict, Tuple, Optional
from core.avl import Node
from core.vertex import Vertex

class RouteOptimizer:

    
    def __init__(self, tracker: 'RouteTracker', manager: 'RouteManager'):

        self.tracker = tracker
        self.manager = manager
        self.optimization_decisions = []  # reg de desiciones tomadas
        self.route_patterns = {}  # patrones identificados
        
    def suggest_optimized_route(self, origin_id: str, destination_id: str) -> Optional[List[Vertex]]:

        decision_log = {
            'origin': origin_id,
            'destination': destination_id,
            'strategy_used': None,
            'details': {}
        }
        
        # buscar ruta exacta frecuente
        frequent_routes = self.tracker.get_most_frequent_routes()
        route_str = f"{origin_id}->{destination_id}"
        
        for route, count in frequent_routes:
            if route == route_str:
                decision_log['strategy_used'] = "Ruta exacta frecuente"
                decision_log['details'] = {
                    'route': route,
                    'frequency': count
                }
                self.optimization_decisions.append(decision_log)
                
                # convertir string de ruta a lista de vértices
                return [Vertex(node_id) for node_id in route.split('->')]
        
        # buscar segmentos comunes
        common_segments = self.analyze_route_patterns()
        best_segment = None
        max_length = 0
        
        for segment in common_segments:
            if origin_id in segment and destination_id in segment:
                idx_origin = segment.index(origin_id)
                idx_dest = segment.index(destination_id)
                
                if idx_origin < idx_dest and len(segment[idx_origin:idx_dest+1]) > max_length:
                    best_segment = segment[idx_origin:idx_dest+1]
                    max_length = len(best_segment)
        
        if best_segment:
            decision_log['strategy_used'] = "Combinación de segmentos conocidos"
            decision_log['details'] = {
                'segment': '->'.join(best_segment),
                'length': len(best_segment)
            }
            self.optimization_decisions.append(decision_log)
            
            return [Vertex(node_id) for node_id in best_segment]
        
        # calcular nueva ruta
        new_route = self.manager.find_route_with_recharge(origin_id, destination_id)
        if new_route and new_route.get('path'):
            decision_log['strategy_used'] = "Nueva ruta calculada"
            decision_log['details'] = {
                'route': '->'.join(v.id for v in new_route['path']),
                'cost': new_route.get('total_cost', 0)
            }
            self.optimization_decisions.append(decision_log)
            
            # registrar la nueva ruta para futuras optimizaciones
            self.tracker.register_route(new_route['path'], new_route.get('total_cost', 0))
            return new_route['path']
        
        # si no se encontro ninguna ruta
        decision_log['strategy_used'] = "No se encontro ruta"
        self.optimization_decisions.append(decision_log)
        return None
    
    def analyze_route_patterns(self) -> List[List[str]]:
        frequent_routes = self.tracker.get_most_frequent_routes(top_n=20)
        patterns = {}
        
        for route_str, count in frequent_routes:
            nodes = route_str.split('->')
            
            # identificar todos los posibles segmentos de la ruta
            for i in range(len(nodes)):
                for j in range(i+1, len(nodes)):
                    segment = '->'.join(nodes[i:j+1])
                    patterns[segment] = patterns.get(segment, 0) + count
        
        # filtrar segmentos significativos (más de 2 nodos y alta frecuencia)
        significant_patterns = [
            segment.split('->') 
            for segment, count in patterns.items() 
            if len(segment.split('->')) > 2 and count > 3
        ]
        
        # ordenar por longitud y frecuencia
        significant_patterns.sort(key=lambda x: (-len(x), -patterns['->'.join(x)]))
        
        # almacenar para uso futuro
        self.route_patterns = {
            'patterns': significant_patterns,
            'stats': {
                'total_patterns': len(significant_patterns),
                'most_common': significant_patterns[0] if significant_patterns else None
            }
        }
        
        return significant_patterns
    
    def get_optimization_report(self) -> Dict[str, Any]:

        strategy_counts = {}
        for decision in self.optimization_decisions:
            strategy = decision['strategy_used']
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        
        # reporte detallado
        report = {
            'summary': {
                'total_optimizations': len(self.optimization_decisions),
                'strategy_distribution': strategy_counts,
                'patterns_identified': self.route_patterns.get('stats', {}).get('total_patterns', 0)
            },
            'recent_decisions': self.optimization_decisions[-5:] if self.optimization_decisions else [],
            'identified_patterns': self.route_patterns.get('patterns', [])[:5]
        }
        
        return report
    
    def _generate_text_report(self) -> str:

        report = self.get_optimization_report()
        text = "=== Reporte de Optimización de Rutas ===\n\n"
        
        #resumen
        text += "Resumen Estadístico:\n"
        text += f"- Optimizaciones totales: {report['summary']['total_optimizations']}\n"
        text += "- Distribución de estrategias:\n"
        for strategy, count in report['summary']['strategy_distribution'].items():
            text += f"  - {strategy}: {count} veces\n"
        text += f"- Patrones identificados: {report['summary']['patterns_identified']}\n\n"
        
        # decisiones recientes
        text += "Últimas 5 decisiones:\n"
        for i, decision in enumerate(report['recent_decisions'], 1):
            text += f"{i}. Origen: {decision['origin']} -> Destino: {decision['destination']}\n"
            text += f"   Estrategia: {decision['strategy_used']}\n"
            if decision['details']:
                text += "   Detalles:\n"
                for key, value in decision['details'].items():
                    text += f"     - {key}: {value}\n"
            text += "\n"
        
        # patrones principales
        if report['identified_patterns']:
            text += "Principales patrones identificados:\n"
            for i, pattern in enumerate(report['identified_patterns'], 1):
                text += f"{i}. {' -> '.join(pattern)}\n"
        
        return text