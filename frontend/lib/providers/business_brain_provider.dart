import 'package:flutter/material.dart';
import '../services/api_service.dart';

class BusinessBrainProvider extends ChangeNotifier {
  Map<String, dynamic> _dailySummary = {};
  Map<String, dynamic> _salesInsight = {};
  bool _isLoading = false;
  String? _error;

  Map<String, dynamic> get dailySummary => _dailySummary;
  Map<String, dynamic> get salesInsight => _salesInsight;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> loadDailySummary() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final res = await ApiService.getDailyBusinessSummary();
      if (res['status'] == 'success') {
        _dailySummary = Map<String, dynamic>.from(res['data'] ?? {});
      }
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> loadSalesInsight({String period = 'today'}) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final res = await ApiService.getSalesInsight(period: period);
      if (res['status'] == 'success') {
        _salesInsight = Map<String, dynamic>.from(res['data'] ?? {});
      }
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
