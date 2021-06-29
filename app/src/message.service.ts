import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { Socket } from 'ngx-socket-io';
// import { map } from 'rxjs/operators';

import { Message } from "./message.type";

@Injectable({
  providedIn: 'root',
})
export class MessageService {
  private _messages: BehaviorSubject<Message[]> = new BehaviorSubject([]);
  public readonly messages: Observable<Message[]> = this._messages.asObservable();

  constructor(private http: HttpClient, private socket: Socket) {
    this.socket.fromEvent<Message[]>('messages').subscribe(
      (result) => this._messages.next(result),
      (err) => console.log("MessageService: constructor(): error calling api", err)
    )
  }

  sendMessage(msg: string) {
    this.socket.emit('send', msg);
  }

  getMessages() {
    //return this.http.get<Message[]>('/assets/messages.json');
    return this.messages;
  }
}
