# -*- coding: utf-8 -*-

# Copyright 2024 Spanish National Research Council (CSIC)
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Tests for CLI fix handling models with missing get_predict_args or get_train_args"""

import unittest

from webargs import fields
from deepaas.model.v2 import wrapper as v2_wrapper


class TestCLIModelHandling(unittest.TestCase):
    """Test CLI functionality with models that have missing methods"""

    def test_model_wrapper_handles_missing_predict_args(self):
        """Test that ModelWrapper handles models without get_predict_args"""
        
        class TrainOnlyModel:
            def get_metadata(self):
                return {"name": "train-only", "version": "1.0"}
            
            def train(self, **kwargs):
                return {"status": "trained"}
                
            def get_train_args(self):
                return {"epochs": fields.Int(required=True)}
            
            # NOTE: Missing get_predict_args method
        
        model = TrainOnlyModel()
        wrapper = v2_wrapper.ModelWrapper("train-only", model, None)
        
        # Should not raise AttributeError
        predict_args = wrapper.get_predict_args()
        train_args = wrapper.get_train_args()
        
        self.assertEqual(predict_args, {})
        self.assertIn("epochs", train_args)

    def test_model_wrapper_handles_missing_train_args(self):
        """Test that ModelWrapper handles models without get_train_args"""
        
        class PredictOnlyModel:
            def get_metadata(self):
                return {"name": "predict-only", "version": "1.0"}
            
            def predict(self, **kwargs):
                return {"prediction": "result"}
                
            def get_predict_args(self):
                return {"data": fields.Str(required=True)}
            
            # NOTE: Missing get_train_args method
        
        model = PredictOnlyModel()
        wrapper = v2_wrapper.ModelWrapper("predict-only", model, None)
        
        # Should not raise AttributeError
        predict_args = wrapper.get_predict_args()
        train_args = wrapper.get_train_args()
        
        self.assertIn("data", predict_args)
        self.assertEqual(train_args, {})

    def test_model_wrapper_handles_missing_both_args(self):
        """Test that ModelWrapper handles models without both args methods"""
        
        class MinimalModel:
            def get_metadata(self):
                return {"name": "minimal", "version": "1.0"}
            
            # NOTE: Missing both get_predict_args and get_train_args methods
        
        model = MinimalModel()
        wrapper = v2_wrapper.ModelWrapper("minimal", model, None)
        
        # Should not raise AttributeError for either method
        predict_args = wrapper.get_predict_args()
        train_args = wrapper.get_train_args()
        
        self.assertEqual(predict_args, {})
        self.assertEqual(train_args, {})

    def test_direct_model_fails_as_expected(self):
        """Test that direct model access fails as expected (validating the problem)"""
        
        class PredictOnlyModel:
            def get_predict_args(self):
                return {"data": fields.Str(required=True)}
            # NOTE: Missing get_train_args method
        
        model = PredictOnlyModel()
        
        # Direct access should work for existing method
        predict_args = model.get_predict_args()
        self.assertIn("data", predict_args)
        
        # Direct access should fail for missing method
        with self.assertRaises(AttributeError):
            model.get_train_args()


if __name__ == '__main__':
    unittest.main()