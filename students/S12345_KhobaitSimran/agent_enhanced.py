"""
Enhanced YSMAI Agent with ML Integration

Combines traditional 3-state FSM with ML predictions for improved decision-making.
"""

import time
from typing import Dict, Optional, Any

try:
    from ml_training_kaggle import MLModelTrainer, ML_AVAILABLE
except ImportError:
    ML_AVAILABLE = False


class EnhancedYSMAI_Agent:
    """
    Enhanced agent combining rule-based FSM with ML predictions.
    
    States:
    - NORMAL: All systems nominal
    - ALERT_HIGH: Temperature high
    - ALERT_LOW: Temperature low
    - ML_PREDICTED_FAULT: ML model detected fault
    """
    
    STATE_NORMAL = "NORMAL"
    STATE_ALERT_HIGH = "ALERT_HIGH"
    STATE_ALERT_LOW = "ALERT_LOW"
    STATE_ML_FAULT = "ML_PREDICTED_FAULT"
    
    def __init__(
        self,
        threshold_high: float = 85.0,
        threshold_low: float = 50.0,
        debounce_sec: float = 1.5,
        use_ml: bool = True
    ):
        """
        Initialize enhanced agent.
        
        Args:
            threshold_high: High temperature threshold (°F)
            threshold_low: Low temperature threshold (°F)
            debounce_sec: Debounce duration (seconds)
            use_ml: Enable ML predictions
        """
        self.threshold_high = threshold_high
        self.threshold_low = threshold_low
        self.debounce_sec = debounce_sec
        
        # State tracking
        self.current_state = self.STATE_NORMAL
        self.last_state = self.STATE_NORMAL
        self.state_timestamp = time.time()
        self.condition_start_time = None
        
        # ML integration
        self.use_ml = use_ml and ML_AVAILABLE
        self.ml_trainer = None
        self.ml_ready = False
        
        if self.use_ml:
            try:
                self.ml_trainer = MLModelTrainer()
                self.ml_trainer.load_all_models()
                self.ml_ready = self.ml_trainer.is_trained
            except Exception as e:
                print(f"⚠ ML integration failed: {e}")
                self.use_ml = False
    
    def update(
        self,
        temp: float,
        timestamp_unix: float,
        rpm: float = 0,
        pressure: float = 0,
        vib: float = 0
    ) -> Dict[str, Any]:
        """
        Update agent state with sensor data.
        
        Args:
            temp: Temperature (°F)
            timestamp_unix: Unix timestamp
            rpm: Engine RPM (optional, for ML)
            pressure: Oil pressure PSI (optional, for ML)
            vib: Vibration mm/s (optional, for ML)
            
        Returns:
            Response dict with state and predictions
        """
        current_time = timestamp_unix
        
        # Rule-based FSM logic
        if temp > self.threshold_high:
            if self.condition_start_time is None:
                self.condition_start_time = current_time
            
            elapsed = current_time - self.condition_start_time
            new_state = self.STATE_ALERT_HIGH if elapsed >= self.debounce_sec else self.current_state
        
        elif temp < self.threshold_low:
            if self.condition_start_time is None:
                self.condition_start_time = current_time
            
            elapsed = current_time - self.condition_start_time
            new_state = self.STATE_ALERT_LOW if elapsed >= self.debounce_sec else self.current_state
        
        else:
            if self.condition_start_time is not None:
                elapsed = current_time - self.condition_start_time
                if elapsed >= self.debounce_sec:
                    new_state = self.STATE_NORMAL
                    self.condition_start_time = None
                else:
                    new_state = self.current_state
            else:
                new_state = self.STATE_NORMAL
        
        state_changed = (new_state != self.current_state)
        if state_changed:
            self.last_state = self.current_state
            self.current_state = new_state
            self.state_timestamp = current_time
            self.condition_start_time = None
        
        # Build response
        response = {
            'timestamp': current_time,
            'temperature': temp,
            'state': self.current_state,
            'state_changed': state_changed,
            'alert_message': self._generate_alert_message(self.current_state),
        }
        
        # Add ML predictions if available
        if self.use_ml and self.ml_ready:
            response['ml_insights'] = self._get_ml_predictions(rpm, pressure, temp, vib)
        else:
            response['ml_insights'] = None
        
        return response
    
    def _generate_alert_message(self, state: str) -> Optional[str]:
        """Generate alert message for state."""
        messages = {
            self.STATE_NORMAL: None,
            self.STATE_ALERT_HIGH: f"⚠️ HIGH TEMPERATURE: exceeds {self.threshold_high}°F",
            self.STATE_ALERT_LOW: f"⚠️ LOW TEMPERATURE: below {self.threshold_low}°F",
            self.STATE_ML_FAULT: "🚨 ML FAULT DETECTION: Abnormal condition detected"
        }
        return messages.get(state)
    
    def _get_ml_predictions(self, rpm: float, pressure: float, temp: float, vib: float) -> Dict[str, Any]:
        """Get ML model predictions."""
        if not self.ml_trainer:
            return None
        
        predictions = {}
        
        # Fault detection
        try:
            fault_result = self.ml_trainer.predict_fault(rpm, pressure, temp, vib)
            predictions['fault_detection'] = {
                'detected': fault_result.get('fault', False),
                'confidence': fault_result.get('confidence', 0.0)
            }
        except Exception as e:
            predictions['fault_detection'] = {'error': str(e)}
        
        # Vibration anomaly
        try:
            vib_result = self.ml_trainer.detect_vibration_anomaly(vib, vib * 0.5)
            predictions['vibration_anomaly'] = {
                'detected': vib_result.get('anomaly', False),
                'score': vib_result.get('score', 0.0)
            }
        except Exception as e:
            predictions['vibration_anomaly'] = {'error': str(e)}
        
        # Pressure prediction
        try:
            if pressure > 0:  # Only predict if flow data available
                pressure_result = self.ml_trainer.predict_pressure(pressure)
                predictions['pressure_prediction'] = pressure_result
        except Exception as e:
            predictions['pressure_prediction'] = {'error': str(e)}
        
        return predictions
    
    def get_state(self) -> str:
        """Get current state."""
        return self.current_state
    
    def get_timestamp(self) -> float:
        """Get state transition timestamp."""
        return self.state_timestamp
    
    def reset(self) -> None:
        """Reset agent to initial state."""
        self.current_state = self.STATE_NORMAL
        self.last_state = self.STATE_NORMAL
        self.state_timestamp = time.time()
        self.condition_start_time = None
    
    def get_debug_state(self) -> Dict[str, Any]:
        """Get full agent state for debugging."""
        return {
            'current_state': self.current_state,
            'last_state': self.last_state,
            'state_timestamp': self.state_timestamp,
            'threshold_high': self.threshold_high,
            'threshold_low': self.threshold_low,
            'debounce_sec': self.debounce_sec,
            'ml_enabled': self.use_ml,
            'ml_ready': self.ml_ready
        }
