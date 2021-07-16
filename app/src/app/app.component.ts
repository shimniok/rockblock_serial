import { Component } from '@angular/core';
import { MessageService } from 'src/app/services/message.service';
import { Message } from 'src/app/types/message.type';
import { Observable } from 'rxjs';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'app';
  messages: Observable<Message[]>;
  signal: Observable<number>;

  constructor (private messageService: MessageService) {
    this.messages = messageService.messages;
    this.signal = messageService.signal;
  }
}
