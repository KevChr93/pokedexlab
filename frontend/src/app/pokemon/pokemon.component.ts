import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-pokemon',
  templateUrl: './pokemon.component.html',
  styleUrls: ['./pokemon.component.scss']
})
export class PokemonComponent implements OnInit {

  records;

  constructor(private http: HttpClient) { }

  ngOnInit() {
    const url = environment.BASE_URL + "api/pokemon";
    console.log(url);
    this.http.get(url).subscribe(data => {
      this.records = data;
      console.log(`Retrieved ${this.records.length} records`);
      console.log(data)
    })
  }

}
