# src/systems/player_behavior_analysis.py
import numpy as np
from typing import Dict, List, Any

class BehaviorPattern:
    def __init__(self, name, description, threshold=0.7):
        self.name = name
        self.description = description
        self.threshold = threshold
        self.features = {}  # Các đặc trưng của pattern

class PlayerBehaviorAnalysis:
    def __init__(self, game):
        self.game = game
        self.conversation_history = {}  # {player_id: [conversations]}
        self.movement_patterns = {}     # {player_id: [movements]}
        self.interaction_stats = {}     # {player_id: {npc_id: count}}
        self.reaction_times = {}        # {player_id: [times]}
        
        # Các mẫu hành vi dự đoán player vs NPC
        self.behavior_patterns = [
            BehaviorPattern(
                "inconsistent_dialogue",
                "Trả lời không nhất quán, đổi chủ đề đột ngột",
                threshold=0.65
            ),
            # src/systems/player_behavior_analysis.py (tiếp theo)
            # Tiếp theo từ phần trước
            BehaviorPattern(
                "strategic_movement",
                "Di chuyển có mục đích rõ ràng",
                threshold=0.7
            ),
            BehaviorPattern(
                "interest_in_clues",
                "Quan tâm đặc biệt đến manh mối và ký ức",
                threshold=0.8
            ),
            BehaviorPattern(
                "avoidance_behavior",
                "Tránh mặt một số NPC nhất định",
                threshold=0.6
            ),
            BehaviorPattern(
                "investigation_focus",
                "Liên tục điều tra và theo dõi",
                threshold=0.75
            )
        ]
    
    def record_conversation(self, player_id, npc_id, dialogue_text, response_time):
        """Ghi nhận cuộc hội thoại của người chơi"""
        if player_id not in self.conversation_history:
            self.conversation_history[player_id] = []
        
        self.conversation_history[player_id].append({
            "npc_id": npc_id,
            "text": dialogue_text,
            "time": self.game.current_time,
            "day": self.game.current_day,
            "response_time": response_time
        })
        
        # Cập nhật thống kê tương tác
        if player_id not in self.interaction_stats:
            self.interaction_stats[player_id] = {}
        
        if npc_id not in self.interaction_stats[player_id]:
            self.interaction_stats[player_id][npc_id] = 0
        
        self.interaction_stats[player_id][npc_id] += 1
        
        # Ghi nhận thời gian phản ứng
        if player_id not in self.reaction_times:
            self.reaction_times[player_id] = []
        
        self.reaction_times[player_id].append(response_time)
    
    def record_movement(self, player_id, position, timestamp):
        """Ghi nhận chuyển động của người chơi"""
        if player_id not in self.movement_patterns:
            self.movement_patterns[player_id] = []
        
        self.movement_patterns[player_id].append({
            "position": position,
            "timestamp": timestamp,
            "day": self.game.current_day,
            "time": self.game.current_time
        })
    
    def analyze_player(self, player_id):
        """Phân tích hành vi của một người chơi"""
        results = {}
        
        # Phân tích hội thoại
        dialogue_features = self._analyze_dialogues(player_id)
        results["dialogue"] = dialogue_features
        
        # Phân tích chuyển động
        movement_features = self._analyze_movements(player_id)
        results["movement"] = movement_features
        
        # Phân tích thống kê tương tác
        interaction_features = self._analyze_interactions(player_id)
        results["interactions"] = interaction_features
        
        # Phân tích thời gian phản ứng
        reaction_features = self._analyze_reaction_times(player_id)
        results["reaction_times"] = reaction_features
        
        # Tính điểm người chơi thật
        player_score = self._calculate_player_score(results)
        results["player_likelihood"] = player_score
        
        return results
    
    def _analyze_dialogues(self, player_id):
        """Phân tích đặc điểm hội thoại"""
        if player_id not in self.conversation_history:
            return {}
        
        dialogues = self.conversation_history[player_id]
        if not dialogues:
            return {}
        
        # Đặc điểm phân tích
        features = {
            "total_dialogues": len(dialogues),
            "unique_npcs": len(set(d["npc_id"] for d in dialogues)),
            "avg_length": sum(len(d["text"]) for d in dialogues) / len(dialogues),
            "question_ratio": sum(1 for d in dialogues if "?" in d["text"]) / len(dialogues),
            "consistency_score": 0.0
        }
        
        # Phân tích tính nhất quán trong hội thoại
        # TODO: Implement consistency analysis using NLP
        
        return features
    
    def _analyze_movements(self, player_id):
        """Phân tích mẫu di chuyển"""
        if player_id not in self.movement_patterns:
            return {}
        
        movements = self.movement_patterns[player_id]
        if len(movements) < 10:  # Cần ít nhất 10 điểm dữ liệu
            return {}
        
        # Tính toán các đặc trưng chuyển động
        positions = [m["position"] for m in movements]
        timestamps = [m["timestamp"] for m in movements]
        
        # Tính tốc độ di chuyển trung bình
        speeds = []
        for i in range(1, len(positions)):
            dx = positions[i][0] - positions[i-1][0]
            dy = positions[i][1] - positions[i-1][1]
            dt = timestamps[i] - timestamps[i-1]
            if dt > 0:
                speed = (dx**2 + dy**2)**0.5 / dt
                speeds.append(speed)
        
        avg_speed = sum(speeds) / len(speeds) if speeds else 0
        
        # Tính bán kính hoạt động
        center_x = sum(p[0] for p in positions) / len(positions)
        center_y = sum(p[1] for p in positions) / len(positions)
        
        radius = sum(((p[0] - center_x)**2 + (p[1] - center_y)**2)**0.5 for p in positions) / len(positions)
        
        # Đếm các lần thay đổi hướng đi
        direction_changes = 0
        for i in range(2, len(positions)):
            prev_dx = positions[i-1][0] - positions[i-2][0]
            prev_dy = positions[i-1][1] - positions[i-2][1]
            
            curr_dx = positions[i][0] - positions[i-1][0]
            curr_dy = positions[i][1] - positions[i-1][1]
            
            # Tính góc giữa hai vector chuyển động
            if prev_dx == 0 and prev_dy == 0 or curr_dx == 0 and curr_dy == 0:
                continue
                
            dot_product = prev_dx*curr_dx + prev_dy*curr_dy
            prev_mag = (prev_dx**2 + prev_dy**2)**0.5
            curr_mag = (curr_dx**2 + curr_dy**2)**0.5
            
            if prev_mag * curr_mag == 0:
                continue
                
            cos_angle = dot_product / (prev_mag * curr_mag)
            cos_angle = max(-1.0, min(1.0, cos_angle))  # Clamp to [-1, 1]
            
            angle = np.arccos(cos_angle)
            
            # Đếm thay đổi hướng lớn
            if angle > np.pi/6:  # Thay đổi hướng > 30 độ
                direction_changes += 1
        
        features = {
            "avg_speed": avg_speed,
            "activity_radius": radius,
            "direction_changes": direction_changes,
            "path_efficiency": self._calculate_path_efficiency(positions)
        }
        
        return features
    
    def _calculate_path_efficiency(self, positions):
        """Tính hiệu quả đường đi (tỷ lệ khoảng cách thẳng / khoảng cách thực tế)"""
        if len(positions) < 2:
            return 1.0
        
        # Khoảng cách thực tế
        actual_distance = 0
        for i in range(1, len(positions)):
            dx = positions[i][0] - positions[i-1][0]
            dy = positions[i][1] - positions[i-1][1]
            actual_distance += (dx**2 + dy**2)**0.5
        
        # Khoảng cách thẳng từ đầu đến cuối
        dx = positions[-1][0] - positions[0][0]
        dy = positions[-1][1] - positions[0][1]
        direct_distance = (dx**2 + dy**2)**0.5
        
        if actual_distance == 0:
            return 1.0
            
        return direct_distance / actual_distance
    
    def _analyze_interactions(self, player_id):
        """Phân tích thống kê tương tác với NPC"""
        if player_id not in self.interaction_stats:
            return {}
        
        stats = self.interaction_stats[player_id]
        if not stats:
            return {}
        
        total_interactions = sum(stats.values())
        npc_count = len(stats)
        
        if npc_count == 0:
            return {"total_interactions": 0, "npc_count": 0}
        
        # Tính độ tập trung tương tác (concentration)
        # Nếu tương tác đều với tất cả NPC -> thấp, nếu tập trung vào 1-2 NPC -> cao
        max_interactions = max(stats.values())
        
        if total_interactions == 0:
            concentration = 0
        else:
            concentration = max_interactions / total_interactions * npc_count / len(self.game.npcs)
        
        features = {
            "total_interactions": total_interactions,
            "npc_count": npc_count,
            "interaction_concentration": concentration,
            "interaction_distribution": {npc: count/total_interactions for npc, count in stats.items()}
        }
        
        return features
    
    def _analyze_reaction_times(self, player_id):
        """Phân tích thời gian phản ứng"""
        if player_id not in self.reaction_times:
            return {}
        
        times = self.reaction_times[player_id]
        if not times:
            return {}
        
        avg_time = sum(times) / len(times)
        variance = sum((t - avg_time)**2 for t in times) / len(times)
        
        # NPC thường có thời gian phản ứng ổn định hơn người thật
        features = {
            "avg_reaction_time": avg_time,
            "reaction_variance": variance,
            "human_likeness": self._calculate_human_likeness(times)
        }
        
        return features
    
    def _calculate_human_likeness(self, reaction_times):
        """Tính mức độ giống con người của thời gian phản ứng"""
        if len(reaction_times) < 5:
            return 0.5  # Không đủ dữ liệu
        
        # Con người thường: 
        # 1. Có variance lớn hơn
        # 2. Có mẫu phù hợp với lognormal distribution
        # 3. Thỉnh thoảng có outliers
        
        avg = sum(reaction_times) / len(reaction_times)
        variance = sum((t - avg)**2 for t in reaction_times) / len(reaction_times)
        
        # Chuẩn hóa
        normalized_variance = min(variance / avg, 5.0) / 5.0
        
        # Kiểm tra sự xuất hiện của outliers
        outlier_threshold = avg * 2
        outlier_count = sum(1 for t in reaction_times if t > outlier_threshold)
        has_outliers = outlier_count > 0
        
        # Kết hợp các yếu tố
        human_score = 0.3 + 0.5 * normalized_variance + 0.2 * (1 if has_outliers else 0)
        
        return human_score
    
    def _calculate_player_score(self, analysis_results):
        """Tính điểm khả năng là người chơi thật"""
        scores = []
        weights = []
        
        # Thời gian phản ứng (rất quan trọng)
        if "reaction_times" in analysis_results and "human_likeness" in analysis_results["reaction_times"]:
            scores.append(analysis_results["reaction_times"]["human_likeness"])
            weights.append(3.0)  # Weight cao
        
        # Hiệu quả đường đi
        if "movement" in analysis_results and "path_efficiency" in analysis_results["movement"]:
            # Người thật thường ít hiệu quả hơn AI
            inefficiency = 1.0 - analysis_results["movement"]["path_efficiency"]
            scores.append(min(inefficiency * 2.0, 1.0))
            weights.append(1.5)
        
        # Tỷ lệ câu hỏi
        if "dialogue" in analysis_results and "question_ratio" in analysis_results["dialogue"]:
            # Người thật thường hỏi nhiều hơn
            question_score = min(analysis_results["dialogue"]["question_ratio"] * 2.0, 1.0)
            scores.append(question_score)
            weights.append(1.0)
        
        # Tính điểm trung bình có trọng số
        if not scores:
            return 0.5  # Giá trị mặc định nếu không có dữ liệu
        
        total_weight = sum(weights)
        weighted_score = sum(s * w for s, w in zip(scores, weights)) / total_weight
        
        return weighted_score
    
    def get_most_likely_players(self):
        """Lấy danh sách nhân vật có khả năng cao nhất là người chơi thật"""
        character_scores = {}
        
        for char_id in self.conversation_history.keys():
            analysis = self.analyze_player(char_id)
            
            # Bỏ qua các nhân vật không đủ dữ liệu
            if "player_likelihood" in analysis:
                character_scores[char_id] = analysis["player_likelihood"]
        
        # Sắp xếp theo điểm số giảm dần
        sorted_chars = sorted(character_scores.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_chars
