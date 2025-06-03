import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

interface DatasetResponse {
  count: number;
  data: any[];
}

interface CompareResponse {
  execution_time_seconds: number;
  total_ecarts: number;
  count_identique: number;
  count_different: number;
  count_nouveau: number;
  data: any[];
}

@Injectable({
  providedIn: 'root'
})
export class DataService {
  private baseUrl = 'http://localhost:8000/spark'; // adapte l'URL selon ton backend

  constructor(private http: HttpClient) {}

  // Dataset A
  getDatasetA(): Observable<DatasetResponse> {
    return this.http.get<DatasetResponse>(`${this.baseUrl}/dataset-a/`);
  }

  generateDatasetA(n: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/dataset-a/`, { nombre: n });
  }

  clearDatasetA(): Observable<any> {
    return this.http.delete(`${this.baseUrl}/dataset-a/`);
  }

  // Dataset B
  getDatasetB(): Observable<DatasetResponse> {
    return this.http.get<DatasetResponse>(`${this.baseUrl}/dataset-b/`);
  }

  generateDatasetB(n: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/dataset-b/`, { nombre: n });
  }

  clearDatasetB(): Observable<any> {
    return this.http.delete(`${this.baseUrl}/dataset-b/`);
  }


  compareDatasets(methode: 'Spark' | 'Django'): Observable<CompareResponse> {
    return this.http.post<CompareResponse>(`${this.baseUrl}/comparer/`, { methode });
  }


  clearEcarts(): Observable<any> {
    return this.http.delete(`${this.baseUrl}/comparer/`);
  }
}
