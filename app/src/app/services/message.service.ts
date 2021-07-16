import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { Socket } from 'ngx-socket-io';
// import { map } from 'rxjs/operators';

import { Message } from '../types/message.type';

@Injectable({
  providedIn: 'root',
})
export class MessageService {
  private _messages: BehaviorSubject<Message[]> = new BehaviorSubject([]);
  public readonly messages: Observable<Message[]> =
    this._messages.asObservable();

  private _signal: BehaviorSubject<number> = new BehaviorSubject(0);
  public readonly signal: Observable<number> = this._signal.asObservable();

  constructor(private http: HttpClient, private socket: Socket) {
    // subscribe to messages events
    this.socket.fromEvent<Message[]>('messages').subscribe(
      (res) => {
        this._messages.next(res);
      },
      (err) =>
        console.log('MessageService: constructor(): error calling api', err)
    );

    // subscribe to signal events
    this.socket.fromEvent<number>('signal').subscribe(
      (res) => {
        console.log('MessageService: signal:', res.valueOf());
        this._signal.next(res);
      },
      (err) =>
        console.log('MessageService: constructor(): error calling api', err)
    );
  }

  sendMessage(msg: string) {
    var m: Message;

    m.text = msg;

    this.socket.emit('send', m);
  }
}
