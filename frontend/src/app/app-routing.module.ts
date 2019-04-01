import { NgModule } from '@angular/core';

import { Routes, RouterModule } from '@angular/router';
import {PokemonComponent} from "./pokemon/pokemon.component";

const routes: Routes = [
  {path: '', redirectTo: '/pokemon', pathMatch: 'full'},
  {
    path: 'pokemon',
    component: PokemonComponent,
    data: { title: 'List of Pokemon' }
  },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
