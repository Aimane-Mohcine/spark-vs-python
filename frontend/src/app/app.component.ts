import {Component, OnInit} from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from "@angular/forms";
import { DataService } from '../data.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, CommonModule, FormsModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {

  // Dataset A
  dataA: any[] = [];
  totalA: number = 0;
  nombreLignesA: number = 100;
  showInputA: boolean = false;
  loadingGererA: boolean = false;
  loadingViderA: boolean = false;
  loadingGenererA: boolean = false;

  // Dataset B
  dataB: any[] = [];
  totalB: number = 0;
  nombreLignesB: number = 100;
  showInputB: boolean = false;
  loadingGererB: boolean = false;
  loadingViderB: boolean = false;
  loadingGenererB: boolean = false;

  // Écarts
  dataEcarts: any[] = [];
  stats = { identiques: 0, differents: 0, nouveaux: 0 };
  showStats = false;
  showTemps = false;
  showProgress = false;
  showClearEcarts = false;
  showMethodSelection = false;
  traitementEnCours = false;
  progressValue = 0;
  tempsTraitement = 0;
  totalEcarts: number = 0;
  constructor(private dataService: DataService) {}

  ngOnInit(): void {
    this.loadDataA();
    this.loadDataB();
  }

  // Dataset A
  loadDataA() {
    this.dataService.getDatasetA().subscribe(res => {
      this.dataA = res.data;
      this.totalA = res.count;
    });
  }

  genererDataA() {
    this.loadingGenererA = true;
    this.dataService.generateDatasetA(this.nombreLignesA).subscribe({
      next: () => {
        this.loadDataA();
        this.showInputA = false;
        this.loadingGenererA = false;
      },
      error: (error) => {
        console.error('Erreur lors de la génération du dataset A:', error);
        this.loadingGenererA = false;
      }
    });
  }

  clearDataA() {
    this.loadingViderA = true;
    this.dataService.clearDatasetA().subscribe({
      next: () => {
        this.loadDataA();
        this.loadingViderA = false;
      },
      error: (error) => {
        console.error('Erreur lors du vidage du dataset A:', error);
        this.loadingViderA = false;
      }
    });
  }

  toggleInputA() {
    this.loadingGererA = true;
    setTimeout(() => {
      this.showInputA = !this.showInputA;
      this.loadingGererA = false;
    }, 500);
  }

  // Dataset B
  loadDataB() {
    this.dataService.getDatasetB().subscribe(res => {
      this.dataB = res.data;
      this.totalB = res.count;
    });
  }

  genererDataB() {
    this.loadingGenererB = true;
    this.dataService.generateDatasetB(this.nombreLignesB).subscribe({
      next: () => {
        this.loadDataB();
        this.showInputB = false;
        this.loadingGenererB = false;
      },
      error: (error) => {
        console.error('Erreur lors de la génération du dataset B:', error);
        this.loadingGenererB = false;
      }
    });
  }

  clearDataB() {
    this.loadingViderB = true;
    this.dataService.clearDatasetB().subscribe({
      next: () => {
        this.loadDataB();
        this.loadingViderB = false;
      },
      error: (error) => {
        console.error('Erreur lors du vidage du dataset B:', error);
        this.loadingViderB = false;
      }
    });
  }

  toggleInputB() {
    this.loadingGererB = true;
    setTimeout(() => {
      this.showInputB = !this.showInputB;
      this.loadingGererB = false;
    }, 500);
  }

  // Analyse d'écarts - NOUVELLE IMPLÉMENTATION AVEC BACKEND
  lancerTraitement() {
    if (this.dataA.length === 0 || this.dataB.length === 0) {
      alert("Veuillez générer les deux datasets avant de lancer l'analyse.");
      return;
    }
    this.showMethodSelection = true;
  }

  traiterAvec(methode: 'Spark' | 'Django') {
    this.traitementEnCours = true;
    this.showMethodSelection = false;
    this.showProgress = true;
    this.progressValue = 0;

    // Simulation visuelle du progress bar pendant l'appel API
    const progressInterval = setInterval(() => {
      if (this.progressValue < 90) {
        this.progressValue += 10;
      }
    }, 200);

    this.dataService.compareDatasets(methode).subscribe({
      next: (response) => {
        clearInterval(progressInterval);
        this.progressValue = 100;

        // Mise à jour des données avec la réponse du backend
        this.dataEcarts = response.data;
        this.totalEcarts = response.total_ecarts; // ← Ajouter cette ligne

        this.stats = {
          identiques: response.count_identique,
          differents: response.count_different,
          nouveaux: response.count_nouveau
        };
        this.tempsTraitement = response.execution_time_seconds
        // Finaliser l'affichage
        setTimeout(() => {
          this.finirTraitement();
        }, 500);
      },
      error: (error) => {
        clearInterval(progressInterval);
        console.error('Erreur lors de l\'analyse:', error);
        alert('Erreur lors de l\'analyse des datasets. Vérifiez la console pour plus de détails.');
        this.traitementEnCours = false;
        this.showProgress = false;
        this.progressValue = 0;
      }
    });
  }

  finirTraitement() {
    this.traitementEnCours = false;
    this.showProgress = false;
    this.showTemps = true;
    this.showClearEcarts = true;
    this.showStats = true;
  }

  clearEcarts() {

    this.dataService.clearEcarts().subscribe({
      next: () => {
        // Réinitialiser les données après succès de l'API
        this.dataEcarts = [];
        this.totalEcarts = 0;
        this.showStats = false;
        this.showTemps = false;
        this.showClearEcarts = false;
        this.stats = { identiques: 0, differents: 0, nouveaux: 0 };
        this.tempsTraitement = 0;
      },
      error: (error) => {
        console.error('Erreur lors de l\'effacement de l\'analyse:', error);
        // Optionnel : afficher un message d'erreur à l'utilisateur
        alert('Erreur lors de l\'effacement de l\'analyse');
      }
    });
  }

  annulerChoixTraitement() {
    this.showMethodSelection = false;
  }

  // Fonction pour formater les nombres avec K, M, etc.
  formatNumber(num: number): string {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(num % 1000000 === 0 ? 0 : 1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(num % 1000 === 0 ? 0 : 1) + 'K';
    }
    return num.toString();
  }
}
