import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Message } from "./message.type";

@Injectable({
  providedIn: 'root'
})
export class MessageService {

  constructor(private http: HttpClient) { }

  getMessages() {
    return this.http.get<Message[]>('/assets/messages.json');
  }
}
